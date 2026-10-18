"""Road-traffic noise model: distance attenuation + blocking + time-of-day factor.

Reference: UK CRTN-style line-source attenuation. All outputs are labelled
"indicative" - this is a simplified estimate, not a certified acoustic survey.
"""
import math

import shapely.geometry

from . import config

_M_PER_DEG_LAT = 111_320.0
_MAX_ROAD_DISTANCE_M = 500.0  # roads farther than this contribute negligibly, skip them
_PEAK_HOURS = {7, 8, 9, 17, 18, 19, 20}
_QUIET_HOURS = {23, 0, 1, 2, 3, 4, 5}


def _m_per_deg_lon(lat_deg: float) -> float:
    return 111_320.0 * math.cos(math.radians(lat_deg))


def _project(lon: float, lat: float) -> tuple[float, float]:
    origin_lon, origin_lat = config.PRECINCT_ORIGIN_LONLAT
    return (lon - origin_lon) * _m_per_deg_lon(origin_lat), (lat - origin_lat) * _M_PER_DEG_LAT


def _project_ring(coords: list[list[float]]) -> list[tuple[float, float]]:
    ring = coords[:-1] if coords[0] == coords[-1] else coords
    return [_project(lon, lat) for lon, lat in ring]


def attenuate(base_db: float, distance_m: float) -> float:
    d = max(distance_m, config.REFERENCE_DISTANCE_M)
    return base_db - 10 * math.log10(d / config.REFERENCE_DISTANCE_M)


def energy_sum_db(levels_db: list[float]) -> float:
    if not levels_db:
        return 0.0
    return 10 * math.log10(sum(10 ** (lvl / 10) for lvl in levels_db))


def rating(db: float) -> str:
    t = config.NOISE_RATING_THRESHOLDS
    if db < t["Quiet"]:
        return "Quiet"
    if db < t["Moderate"]:
        return "Moderate"
    return "Noisy"


def _hour_bucket(hour: int) -> str:
    if hour in _PEAK_HOURS:
        return "peak"
    if hour in _QUIET_HOURS:
        return "quiet"
    return "normal"


def hourly_db_for_unit(unit_feature: dict, roads_geojson: dict, buildings_geojson: dict) -> dict:
    unit_id = unit_feature["properties"]["unit_id"]
    unit_poly = shapely.geometry.Polygon(_project_ring(unit_feature["geometry"]["coordinates"][0]))
    unit_point = unit_poly.centroid

    other_buildings = [
        shapely.geometry.Polygon(_project_ring(f["geometry"]["coordinates"][0]))
        for f in buildings_geojson["features"]
        if f["properties"]["unit_id"] != unit_id
    ]

    contributions = []  # (attenuated_db, label)
    for road in roads_geojson["features"]:
        highway = road["properties"]["highway"]
        base_db = config.ROAD_BASE_DB.get(highway)
        if base_db is None:
            continue
        line = shapely.geometry.LineString([_project(lon, lat) for lon, lat in road["geometry"]["coordinates"]])
        nearest_pt = line.interpolate(line.project(unit_point))
        distance_m = unit_point.distance(nearest_pt)
        if distance_m > _MAX_ROAD_DISTANCE_M:
            continue

        db = attenuate(base_db, distance_m)
        sight_line = shapely.geometry.LineString([nearest_pt, unit_point])
        if any(sight_line.crosses(b) for b in other_buildings):
            db -= config.BARRIER_ATTENUATION_DB

        label = road["properties"].get("name") or highway
        contributions.append((db, f"{label} ({highway})"))

    base_level = energy_sum_db([db for db, _ in contributions]) if contributions else 35.0
    dominant_source = max(contributions, key=lambda c: c[0])[1] if contributions else None

    hourly_db = {
        f"{hour:02d}": round(base_level + config.TRAFFIC_PROFILE[_hour_bucket(hour)], 1) for hour in range(24)
    }
    representative_db = base_level + config.TRAFFIC_PROFILE["normal"]

    return {
        "hourly_db": hourly_db,
        "rating": rating(representative_db),
        "dominant_source": dominant_source,
        "indicative": True,
    }
