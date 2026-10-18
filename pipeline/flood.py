"""Relative elevation (Copernicus DEM GLO-30) + proximity to waterways -> indicative flood rating."""
from . import config


def relative_elevation(unit_elevation_m: float, surrounding_median_m: float) -> float:
    return unit_elevation_m - surrounding_median_m


def rating(relative_elevation_m: float, nearest_waterway_m: float) -> tuple[str, list[str]]:
    t = config.FLOOD_RATING_THRESHOLDS
    reasons = []
    if (
        relative_elevation_m >= t["Low"]["min_relative_elevation_m"]
        and nearest_waterway_m >= t["Low"]["min_waterway_dist_m"]
    ):
        reasons.append(f"{relative_elevation_m:.1f}m above surrounding median, {nearest_waterway_m:.0f}m from nearest waterway")
        return "Low", reasons
    if (
        relative_elevation_m >= t["Medium"]["min_relative_elevation_m"]
        and nearest_waterway_m >= t["Medium"]["min_waterway_dist_m"]
    ):
        reasons.append(f"{relative_elevation_m:.1f}m above surrounding median, {nearest_waterway_m:.0f}m from nearest waterway")
        return "Medium", reasons
    reasons.append(f"Only {relative_elevation_m:.1f}m above surrounding median, {nearest_waterway_m:.0f}m from nearest waterway")
    return "High", reasons


def unit_flood_profile(unit_geometry, dem_raster, waterways_geojson) -> dict:
    # TODO: sample DEM within config.RELATIVE_ELEVATION_RADIUS_M, nearest waterway distance,
    # return {"rating", "relative_elevation_m", "nearest_waterway_m", "reasons", "indicative": True}
    raise NotImplementedError
