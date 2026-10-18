"""Fetch roads, waterways and amenities around the precinct via Overpass/OSMnx."""
import json
import urllib.request
from pathlib import Path

from . import config

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "CubaDulu-hackathon-pipeline/1.0 (contact: whafiz012@gmail.com)"


def _overpass(query: str) -> dict:
    req = urllib.request.Request(OVERPASS_URL, data=f"data={query}".encode(), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def fetch_roads(bbox: tuple[float, float, float, float], cache_path: Path | None = None) -> dict:
    """bbox: (lon_min, lat_min, lon_max, lat_max). Returns a GeoJSON FeatureCollection of ways."""
    cache_path = cache_path or (RAW_DIR / "roads.geojson")
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))

    lon_min, lat_min, lon_max, lat_max = bbox
    query = f'[out:json];way["highway"]({lat_min},{lon_min},{lat_max},{lon_max});out geom;'
    raw = _overpass(query)

    features = []
    for el in raw["elements"]:
        if el.get("type") != "way" or "geometry" not in el:
            continue
        highway = el["tags"].get("highway")
        if highway not in config.ROAD_BASE_DB:
            continue  # skip footways/service/cycleways etc. - not traffic noise sources
        features.append({
            "type": "Feature",
            "properties": {
                "highway": highway,
                "name": el["tags"].get("name"),
                "osm_id": el["id"],
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [[pt["lon"], pt["lat"]] for pt in el["geometry"]],
            },
        })

    fc = {"type": "FeatureCollection", "features": features}
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(fc, indent=2, ensure_ascii=False), encoding="utf-8")
    return fc


def fetch_waterways(bbox: tuple[float, float, float, float]) -> dict:
    # TODO: Overpass query for waterway=*, save to data/raw/waterways.geojson
    raise NotImplementedError


def fetch_amenities(bbox: tuple[float, float, float, float]) -> dict:
    # TODO: Overpass query for amenity=school|clinic|place_of_worship|supermarket, leisure=park
    raise NotImplementedError


if __name__ == "__main__":
    fetch_roads(config.PRECINCT_BBOX)
