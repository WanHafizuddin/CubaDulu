"""Walking time to nearest amenity per type, via OSMnx walk network shortest path."""
import math
from pathlib import Path

import networkx as nx
import osmnx as ox

from . import config

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
_M_PER_DEG_LAT = 111_320.0


def _m_per_deg_lon(lat_deg: float) -> float:
    return 111_320.0 * math.cos(math.radians(lat_deg))


def _distance_m(lonlat_a: tuple[float, float], lonlat_b: tuple[float, float]) -> float:
    lon_a, lat_a = lonlat_a
    lon_b, lat_b = lonlat_b
    mid_lat = (lat_a + lat_b) / 2
    dx = (lon_b - lon_a) * _m_per_deg_lon(mid_lat)
    dy = (lat_b - lat_a) * _M_PER_DEG_LAT
    return math.hypot(dx, dy)


def build_walk_graph(center_lonlat: tuple[float, float], radius_m: float, cache_path: Path | None = None):
    """Cached to disk - building this graph takes ~1 minute, run it once per precinct."""
    cache_path = cache_path or (RAW_DIR / "walk_graph.graphml")
    if cache_path.exists():
        return ox.load_graphml(cache_path)

    lon, lat = center_lonlat
    graph = ox.graph_from_point((lat, lon), dist=radius_m + 200, network_type="walk")
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, cache_path)
    return graph


def nearest_amenity(unit_lonlat: tuple[float, float], amenities_geojson: dict, amenity_type: str) -> dict | None:
    candidates = [f for f in amenities_geojson["features"] if f["properties"]["amenity_type"] == amenity_type]
    if not candidates:
        return None
    nearest = min(candidates, key=lambda f: _distance_m(unit_lonlat, tuple(f["geometry"]["coordinates"])))
    lon, lat = nearest["geometry"]["coordinates"]
    return {"name": nearest["properties"]["name"], "point": (lon, lat)}


def walk_minutes(unit_lonlat: tuple[float, float], amenity_lonlat: tuple[float, float], walk_graph) -> float | None:
    orig = ox.distance.nearest_nodes(walk_graph, unit_lonlat[0], unit_lonlat[1])
    dest = ox.distance.nearest_nodes(walk_graph, amenity_lonlat[0], amenity_lonlat[1])
    try:
        length_m = nx.shortest_path_length(walk_graph, orig, dest, weight="length")
    except nx.NetworkXNoPath:
        return None
    return round(length_m / config.WALK_SPEED_M_PER_MIN, 1)


def unit_amenities(unit_lonlat: tuple[float, float], amenities_geojson: dict, walk_graph) -> dict:
    result = {}
    for amenity_type in config.AMENITY_TYPES:
        amenity = nearest_amenity(unit_lonlat, amenities_geojson, amenity_type)
        if amenity is None:
            continue
        minutes = walk_minutes(unit_lonlat, amenity["point"], walk_graph)
        if minutes is None:
            continue
        result[amenity_type] = {"name": amenity["name"], "walk_min": minutes}
    return result
