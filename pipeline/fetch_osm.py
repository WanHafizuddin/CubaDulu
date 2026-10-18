"""Fetch roads, waterways and amenities around the precinct via Overpass/OSMnx."""
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"


def fetch_roads(bbox: tuple[float, float, float, float]) -> dict:
    # TODO: Overpass query for highway=* ways within bbox, save to data/raw/roads.geojson
    raise NotImplementedError


def fetch_waterways(bbox: tuple[float, float, float, float]) -> dict:
    # TODO: Overpass query for waterway=*, save to data/raw/waterways.geojson
    raise NotImplementedError


def fetch_amenities(bbox: tuple[float, float, float, float]) -> dict:
    # TODO: Overpass query for amenity=school|clinic|place_of_worship|supermarket, leisure=park
    raise NotImplementedError


if __name__ == "__main__":
    pass
