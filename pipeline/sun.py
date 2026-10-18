"""Sunlit hours per facade via pvlib sun position + raycasting against building geometry."""
from . import config


def sun_position(lat: float, lon: float, when) -> tuple[float, float]:
    # TODO: pvlib.solarposition, return (azimuth_deg, elevation_deg) in config.TIMEZONE
    raise NotImplementedError


def build_scene(units_geojson: dict):
    # TODO: trimesh scene from extruded footprints (height_m per unit)
    raise NotImplementedError


def facade_sun_hours(unit_id: str, scene, geojson_feature: dict, date) -> dict:
    # TODO: sample points per facade (config.FACADE_DIRECTIONS) + roof, raycast toward
    # the sun each hour (config.SUN_HOURS_START..SUN_HOURS_END), unblocked + facing sun -> sunlit
    raise NotImplementedError


def heat_rating(afternoon_sun_hours_after_2pm: float) -> str:
    t = config.HEAT_RATING_THRESHOLDS
    if afternoon_sun_hours_after_2pm < t["Low"]:
        return "Low"
    if afternoon_sun_hours_after_2pm < t["Moderate"]:
        return "Moderate"
    return "High"
