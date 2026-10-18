"""Sunlit hours per facade via pvlib sun position + raycasting against building geometry.

Buildings are extruded footprints in a local East/North/Up metre frame (origin =
config.PRECINCT_ORIGIN_LONLAT). Facades are the footprint polygon's own edges —
for a mid-row terrace unit that naturally makes party walls come out near-zero
sunlit hours, since the neighbouring building's mesh blocks the ray.
"""
import math
from datetime import datetime
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import shapely.geometry
import trimesh
from pvlib import solarposition

from . import config

_M_PER_DEG_LAT = 111_320.0
_RAY_EPS = 0.05  # metres, pushes ray origin off the facade surface to dodge self-hits
_MAX_RAY_DISTANCE = 100_000.0  # sun treated as effectively infinite


def _m_per_deg_lon(lat_deg: float) -> float:
    return 111_320.0 * math.cos(math.radians(lat_deg))


def _project(lon: float, lat: float) -> tuple[float, float]:
    """lon/lat (deg) -> local (east_m, north_m) relative to config.PRECINCT_ORIGIN_LONLAT."""
    origin_lon, origin_lat = config.PRECINCT_ORIGIN_LONLAT
    east = (lon - origin_lon) * _m_per_deg_lon(origin_lat)
    north = (lat - origin_lat) * _M_PER_DEG_LAT
    return east, north


def _footprint_xy(feature: dict) -> list[tuple[float, float]]:
    """Exterior ring of a unit's footprint, local metres, closing point dropped."""
    ring = feature["geometry"]["coordinates"][0]
    pts = [_project(lon, lat) for lon, lat in ring]
    if pts[0] == pts[-1]:
        pts = pts[:-1]
    return pts


def sun_position(lat: float, lon: float, when: datetime) -> tuple[float, float]:
    """Sun azimuth (deg clockwise from north) and apparent elevation (deg) at a local time."""
    tz = ZoneInfo(config.TIMEZONE)
    if when.tzinfo is None:
        when = when.replace(tzinfo=tz)
    pos = solarposition.get_solarposition(pd.DatetimeIndex([when]), lat, lon)
    row = pos.iloc[0]
    return float(row["azimuth"]), float(row["apparent_elevation"])


def _sun_direction(azimuth_deg: float, elevation_deg: float) -> np.ndarray:
    """Unit vector pointing from the ground toward the sun, in local (east, north, up)."""
    az = math.radians(azimuth_deg)
    el = math.radians(elevation_deg)
    return np.array([
        math.cos(el) * math.sin(az),
        math.cos(el) * math.cos(az),
        math.sin(el),
    ])


def build_scene(units_geojson: dict) -> trimesh.Trimesh:
    """Combined mesh of every unit's footprint extruded to height_m, in local metres."""
    meshes = []
    for feature in units_geojson["features"]:
        xy = _footprint_xy(feature)
        height = feature["properties"]["height_m"]
        polygon = shapely.geometry.Polygon(xy)
        if not polygon.is_valid or polygon.area <= 0:
            continue
        mesh = trimesh.creation.extrude_polygon(polygon, height)
        meshes.append(mesh)
    if not meshes:
        return trimesh.Trimesh()
    return trimesh.util.concatenate(meshes)


def _bearing_to_cardinal(bearing_deg: float) -> str:
    b = bearing_deg % 360
    if b >= 315 or b < 45:
        return "N"
    if b < 135:
        return "E"
    if b < 225:
        return "S"
    return "W"


def _facade_edges(xy: list[tuple[float, float]], height_m: float):
    """Yield (cardinal_label, sample_points, outward_normal) for each footprint edge.

    Sample points sit at FACADE_SAMPLE_HEIGHT_FRACTION * height_m, evenly spaced
    along the edge (excluding the corners, where two facades would overlap).
    """
    n = len(xy)
    cx = sum(p[0] for p in xy) / n
    cy = sum(p[1] for p in xy) / n
    z = height_m * config.FACADE_SAMPLE_HEIGHT_FRACTION
    k = config.FACADE_SAMPLE_POINTS_PER_EDGE

    for i in range(n):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % n]
        edge_dx, edge_dy = x2 - x1, y2 - y1
        length = math.hypot(edge_dx, edge_dy)
        if length == 0:
            continue
        # two candidate normals; keep the one pointing away from the polygon centroid
        nx, ny = edge_dy / length, -edge_dx / length
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        if (nx * (mid_x - cx) + ny * (mid_y - cy)) < 0:
            nx, ny = -nx, -ny
        bearing = math.degrees(math.atan2(nx, ny)) % 360  # atan2(east, north)

        points = []
        for j in range(1, k + 1):
            t = j / (k + 1)
            points.append(np.array([x1 + edge_dx * t, y1 + edge_dy * t, z]))

        yield _bearing_to_cardinal(bearing), points, np.array([nx, ny, 0.0])


def facade_sun_hours(unit_id: str, scene: trimesh.Trimesh, geojson_feature: dict, date) -> dict:
    """Hour-by-hour raycast for one unit's facades + roof over config.SUN_HOURS_START..END.

    Returns facade_sun_hours (N/E/S/W -> lit hour count), roof_sun_hours, hourly_sunlit
    ({"07": ["E"], ...}), and west_afternoon_sun_hours (west-facade hours lit from 14:00,
    the input heat.heat_rating() expects).
    """
    # use the footprint centroid (good enough at this scale) for sun position
    xy = _footprint_xy(geojson_feature)
    centroid_x = sum(p[0] for p in xy) / len(xy)
    centroid_y = sum(p[1] for p in xy) / len(xy)
    origin_lon, origin_lat = config.PRECINCT_ORIGIN_LONLAT
    lat = origin_lat + centroid_y / _M_PER_DEG_LAT
    lon = origin_lon + centroid_x / _m_per_deg_lon(origin_lat)

    height = geojson_feature["properties"]["height_m"]
    facades = list(_facade_edges(xy, height))
    roof_points = [np.array([centroid_x, centroid_y, height])]

    facade_hours = {d: 0 for d in config.FACADE_DIRECTIONS}
    roof_hours = 0
    hourly_sunlit: dict[str, list[str]] = {}
    west_afternoon_hours = 0

    tz = ZoneInfo(config.TIMEZONE)
    has_tri = len(scene.faces) > 0

    for hour in range(config.SUN_HOURS_START, config.SUN_HOURS_END + 1):
        when = datetime(date.year, date.month, date.day, hour, 0, tzinfo=tz)
        azimuth, elevation = sun_position(lat, lon, when)
        if elevation <= 0:
            continue
        sun_dir = _sun_direction(azimuth, elevation)
        lit_this_hour = []

        for label, points, normal in facades:
            if np.dot(normal[:2], sun_dir[:2]) <= 0:
                continue
            lit = _majority_unblocked(scene, points, normal, sun_dir, has_tri)
            if lit:
                facade_hours[label] += 1
                lit_this_hour.append(label)
                if label == "W" and hour >= 14:
                    west_afternoon_hours += 1

        if sun_dir[2] > 0:  # anything above horizon reaches the roof unless another block is taller
            if _majority_unblocked(scene, roof_points, np.array([0.0, 0.0, 1.0]), sun_dir, has_tri):
                roof_hours += 1
                lit_this_hour.append("roof")

        if lit_this_hour:
            hourly_sunlit[f"{hour:02d}"] = lit_this_hour

    return {
        "facade_sun_hours": facade_hours,
        "roof_sun_hours": roof_hours,
        "hourly_sunlit": hourly_sunlit,
        "west_afternoon_sun_hours": west_afternoon_hours,
    }


def _majority_unblocked(scene, points, normal, sun_dir, has_tri) -> bool:
    if not has_tri:
        return True
    origins = np.array([p + normal * _RAY_EPS + np.array([0, 0, _RAY_EPS]) for p in points])
    directions = np.tile(sun_dir, (len(points), 1))
    hits = scene.ray.intersects_any(origins, directions)
    unblocked = sum(1 for h in hits if not h)
    return unblocked / len(points) >= 0.5


def heat_rating(afternoon_sun_hours_after_2pm: float) -> str:
    t = config.HEAT_RATING_THRESHOLDS
    if afternoon_sun_hours_after_2pm < t["Low"]:
        return "Low"
    if afternoon_sun_hours_after_2pm < t["Moderate"]:
        return "Moderate"
    return "High"
