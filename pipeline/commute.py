"""Door-to-door commute. Cached once per precinct centroid per destination.

Routed via OSRM's public demo server (no API key, no traffic data) - the spec's
documented fallback when GOOGLE_MAPS_API_KEY isn't set. Swap route_minutes() for
the Google Routes API once a key is available for traffic-aware am/pm timing;
until then am_min and pm_min come out identical.
"""
import json
import urllib.parse
import urllib.request
from pathlib import Path

from . import config

CACHE_PATH = Path(__file__).parent.parent / "data" / "raw" / "commute_cache.json"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving/{o_lon},{o_lat};{d_lon},{d_lat}"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CubaDulu-hackathon-pipeline/1.0 (contact: whafiz012@gmail.com)"

# (lat, lon) for the handoff doc's default destinations, geocoded via Nominatim.
DEFAULT_DESTINATION_COORDS: dict[str, tuple[float, float]] = {
    "KL Sentral": (3.1325847, 101.6879963),
    "Putrajaya": (2.9384381, 101.6922300),
    "KLIA": (2.7448046, 101.7074480),
    "Cyberjaya": (2.9338908, 101.6455587),
    "UPM": (2.9918365, 101.7206770),
}


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def geocode(place: str) -> tuple[float, float]:
    params = urllib.parse.urlencode({"q": place, "format": "jsonv2", "limit": 1})
    req = urllib.request.Request(f"{NOMINATIM_URL}?{params}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        results = json.loads(resp.read())
    if not results:
        raise ValueError(f"could not geocode {place!r}")
    return float(results[0]["lat"]), float(results[0]["lon"])


def route_minutes(origin: tuple[float, float], destination: tuple[float, float], departure: str) -> float:
    del departure  # OSRM's demo server ignores departure time - no traffic model
    o_lat, o_lon = origin
    d_lat, d_lon = destination
    url = OSRM_URL.format(o_lon=o_lon, o_lat=o_lat, d_lon=d_lon, d_lat=d_lat) + "?overview=false"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM routing failed: {data.get('message', data.get('code'))}")
    return round(data["routes"][0]["duration"] / 60, 1)


def commute_for_precinct(centroid: tuple[float, float]) -> dict:
    """centroid: (lat, lon). Returns {destination_name: {am_min, pm_min}}, cached."""
    cache = _load_cache()
    key = f"{centroid[0]:.5f},{centroid[1]:.5f}"
    if key in cache and "destinations" in cache[key]:
        return cache[key]["destinations"]

    result = {}
    for dest_name, dest_coords in DEFAULT_DESTINATION_COORDS.items():
        result[dest_name] = {
            "am_min": route_minutes(centroid, dest_coords, config.COMMUTE_DEPARTURE_AM),
            "pm_min": route_minutes(centroid, dest_coords, config.COMMUTE_DEPARTURE_PM),
        }
    cache.setdefault(key, {})["destinations"] = result
    _save_cache(cache)
    return result


def commute_to_custom_destination(centroid: tuple[float, float], place: str) -> dict:
    """centroid: (lat, lon). Geocodes `place` once, then caches by precinct + place name."""
    cache = _load_cache()
    key = f"{centroid[0]:.5f},{centroid[1]:.5f}"
    custom = cache.setdefault(key, {}).setdefault("custom", {})
    if place in custom:
        return custom[place]

    dest_coords = geocode(place)
    result = {
        "am_min": route_minutes(centroid, dest_coords, config.COMMUTE_DEPARTURE_AM),
        "pm_min": route_minutes(centroid, dest_coords, config.COMMUTE_DEPARTURE_PM),
    }
    custom[place] = result
    _save_cache(cache)
    return result
