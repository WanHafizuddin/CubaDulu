"""Run the full pipeline: data/precinct.geojson -> data/processed/units_livability.json."""
import json
from datetime import date
from pathlib import Path

from . import amenities, commute, config, fetch_osm, flood, noise, sun

PRECINCT_PATH = Path(__file__).parent.parent / "data" / "precinct.geojson"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "processed" / "units_livability.json"


def main():
    precinct = json.loads(PRECINCT_PATH.read_text(encoding="utf-8"))
    scene = sun.build_scene(precinct)
    equinox = date.fromisoformat(config.SUN_REFERENCE_DATES["equinox"])
    roads = fetch_osm.fetch_roads(config.NOISE_ROAD_SEARCH_BBOX)

    records = []
    for feature in precinct["features"]:
        unit_id = feature["properties"]["unit_id"]

        sun_result = sun.facade_sun_hours(unit_id, scene, feature, equinox)
        afternoon_hours = sun_result["west_afternoon_sun_hours"]
        noise_result = noise.hourly_db_for_unit(feature, roads, precinct)

        # TODO: wire up flood.unit_flood_profile, commute.commute_for_precinct,
        # amenities.unit_amenities per unit.
        records.append({
            "unit_id": unit_id,
            "unit_type": feature["properties"]["unit_type"],
            "levels": feature["properties"]["levels"],
            "height_m": feature["properties"]["height_m"],
            "front_orientation_deg": feature["properties"]["front_orientation_deg"],
            "price_rm": feature["properties"]["price_rm"],
            "row": feature["properties"]["row"],
            "geometry": feature["geometry"],
            "sun": {
                "facade_sun_hours": sun_result["facade_sun_hours"],
                "roof_sun_hours": sun_result["roof_sun_hours"],
                "afternoon_sun_hours_after_2pm": afternoon_hours,
                "heat_rating": sun.heat_rating(afternoon_hours),
                "hourly_sunlit": sun_result["hourly_sunlit"],
                "indicative": True,
            },
            "noise": noise_result,
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(records)} units to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
