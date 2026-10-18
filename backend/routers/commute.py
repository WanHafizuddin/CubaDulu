import json
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/commute", tags=["commute"])

# Mirrors pipeline/config.py's PRECINCT_ORIGIN_LONLAT (lon, lat) - see data/raw/location_notes.md.
PRECINCT_CENTROID_LATLON = (2.8443, 101.70285)
CACHE_PATH = Path(__file__).parent.parent.parent / "data" / "raw" / "commute_cache.json"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving/{o_lon},{o_lat};{d_lon},{d_lat}"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CubaDulu-hackathon-backend/1.0 (contact: whafiz012@gmail.com)"


class CustomCommuteRequest(BaseModel):
    destination: str


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def _geocode(place: str) -> tuple[float, float]:
    params = urllib.parse.urlencode({"q": place, "format": "jsonv2", "limit": 1})
    req = urllib.request.Request(f"{NOMINATIM_URL}?{params}", headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        results = json.loads(resp.read())
    if not results:
        raise ValueError(f"could not geocode {place!r}")
    return float(results[0]["lat"]), float(results[0]["lon"])


def _route_minutes(origin: tuple[float, float], destination: tuple[float, float]) -> float:
    # OSRM's public demo server, no traffic model - see pipeline/commute.py for the same
    # fallback. Swap in Google Routes (GOOGLE_MAPS_API_KEY) for traffic-aware timing.
    o_lat, o_lon = origin
    d_lat, d_lon = destination
    url = OSRM_URL.format(o_lon=o_lon, o_lat=o_lat, d_lon=d_lon, d_lat=d_lat) + "?overview=false"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
    if data.get("code") != "Ok":
        raise RuntimeError(f"OSRM routing failed: {data.get('message', data.get('code'))}")
    return round(data["routes"][0]["duration"] / 60, 1)


@router.post("/custom")
def custom_commute(req: CustomCommuteRequest):
    lat, lon = PRECINCT_CENTROID_LATLON
    cache = _load_cache()
    key = f"{lat:.5f},{lon:.5f}"
    custom = cache.setdefault(key, {}).setdefault("custom", {})

    if req.destination not in custom:
        dest_coords = _geocode(req.destination)
        minutes = _route_minutes(PRECINCT_CENTROID_LATLON, dest_coords)
        custom[req.destination] = {"am_min": minutes, "pm_min": minutes}
        _save_cache(cache)

    return {"destination": req.destination, **custom[req.destination]}
