"""Run the full pipeline: data/precinct.geojson -> data/processed/units_livability.json."""
import json
from pathlib import Path

from . import amenities, commute, fetch_osm, flood, noise, sun

PRECINCT_PATH = Path(__file__).parent.parent / "data" / "precinct.geojson"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "units_livability.json"


def main():
    precinct = json.loads(PRECINCT_PATH.read_text())
    records = []

    for feature in precinct["features"]:
        unit_id = feature["properties"]["unit_id"]
        # TODO: wire up sun.facade_sun_hours, noise.hourly_db_for_unit,
        # flood.unit_flood_profile, commute.commute_for_precinct, amenities.unit_amenities
        # per unit and assemble the record shape documented in the project handoff.
        records.append({"unit_id": unit_id})

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(records, indent=2))
    print(f"Wrote {len(records)} units to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
