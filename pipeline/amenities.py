"""Walking time to nearest amenity per type, via OSMnx walk network shortest path."""
from . import config


def nearest_amenity(unit_point, amenities_geojson: dict, amenity_type: str) -> dict | None:
    # TODO: filter amenities_geojson by amenity_type, find nearest within
    # config.AMENITY_SEARCH_RADIUS_M
    raise NotImplementedError


def walk_minutes(unit_point, amenity_point, walk_graph) -> float:
    # TODO: OSMnx shortest path on walk network, distance_m / config.WALK_SPEED_M_PER_MIN
    raise NotImplementedError


def unit_amenities(unit_point, amenities_geojson: dict, walk_graph) -> dict:
    result = {}
    for amenity_type in config.AMENITY_TYPES:
        amenity = nearest_amenity(unit_point, amenities_geojson, amenity_type)
        if amenity is None:
            continue
        result[amenity_type] = {
            "name": amenity.get("name"),
            "walk_min": walk_minutes(unit_point, amenity["point"], walk_graph),
        }
    return result
