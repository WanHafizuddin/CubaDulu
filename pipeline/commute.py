"""Door-to-door commute via Google Routes API. Cached once per precinct centroid per destination."""
import json
import os
from pathlib import Path

from . import config

CACHE_PATH = Path(__file__).parent.parent / "data" / "raw" / "commute_cache.json"


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def route_minutes(origin: tuple[float, float], destination: str, departure: str) -> float:
    # TODO: call Google Routes API (GOOGLE_MAPS_API_KEY env var), traffic-aware,
    # fall back to OpenRouteService (no traffic) if key missing
    raise NotImplementedError


def commute_for_precinct(centroid: tuple[float, float]) -> dict:
    cache = _load_cache()
    key = f"{centroid[0]:.5f},{centroid[1]:.5f}"
    if key in cache:
        return cache[key]

    result = {}
    for dest in config.DEFAULT_DESTINATIONS:
        result[dest] = {
            "am_min": route_minutes(centroid, dest, config.COMMUTE_DEPARTURE_AM),
            "pm_min": route_minutes(centroid, dest, config.COMMUTE_DEPARTURE_PM),
        }
    cache[key] = result
    _save_cache(cache)
    return result
