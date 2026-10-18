"""Road-traffic noise model: distance attenuation + blocking + time-of-day factor."""
import math

from . import config


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


def hourly_db_for_unit(unit_geometry, roads_geojson, buildings_geojson) -> dict:
    # TODO: for each road segment, base_db by config.ROAD_BASE_DB[highway class],
    # attenuate() by distance, subtract config.BARRIER_ATTENUATION_DB if line-of-sight
    # blocked by another building, energy_sum_db() across roads, apply
    # config.TRAFFIC_PROFILE multiplier per hour bucket
    raise NotImplementedError
