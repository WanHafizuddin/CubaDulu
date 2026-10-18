import json
from pathlib import Path

import pytest

from .. import config, noise

PRECINCT_PATH = Path(__file__).parent.parent.parent / "data" / "precinct.geojson"


@pytest.fixture(scope="module")
def precinct():
    return json.loads(PRECINCT_PATH.read_text(encoding="utf-8"))


def feature(precinct, unit_id):
    return next(f for f in precinct["features"] if f["properties"]["unit_id"] == unit_id)


def test_attenuate_3db_per_doubling():
    base = noise.attenuate(70, 10)
    doubled = noise.attenuate(70, 20)
    assert base - doubled == pytest.approx(3.01, abs=0.05)


def test_attenuate_floors_at_reference_distance():
    assert noise.attenuate(70, 1) == noise.attenuate(70, config.REFERENCE_DISTANCE_M)


def test_energy_sum_db_doubles_for_two_equal_sources():
    combined = noise.energy_sum_db([60, 60])
    assert combined == pytest.approx(63.01, abs=0.05)


def test_energy_sum_db_empty():
    assert noise.energy_sum_db([]) == 0.0


def test_rating_thresholds():
    t = config.NOISE_RATING_THRESHOLDS
    assert noise.rating(t["Quiet"] - 1) == "Quiet"
    assert noise.rating(t["Quiet"]) == "Moderate"
    assert noise.rating(t["Moderate"] - 1) == "Moderate"
    assert noise.rating(t["Moderate"]) == "Noisy"


def test_hour_bucket_offsets_match_traffic_profile():
    assert noise._hour_bucket(8) == "peak"
    assert noise._hour_bucket(18) == "peak"
    assert noise._hour_bucket(14) == "normal"
    assert noise._hour_bucket(2) == "quiet"
    assert noise._hour_bucket(23) == "quiet"


def test_hourly_db_for_real_unit_has_all_24_hours(precinct):
    roads = json.loads((Path(__file__).parent.parent.parent / "data" / "raw" / "roads.geojson").read_text(encoding="utf-8"))
    result = noise.hourly_db_for_unit(feature(precinct, "A-13"), roads, precinct)
    assert set(result["hourly_db"].keys()) == {f"{h:02d}" for h in range(24)}
    assert result["indicative"] is True
    # peak hour should read louder than the quiet small hours
    assert result["hourly_db"]["08"] > result["hourly_db"]["23"]


def test_barrier_attenuation_reduces_level_when_blocked():
    # A road 100m west of a unit, with ANOTHER building sitting directly between them.
    unit = {
        "properties": {"unit_id": "T-1"},
        "geometry": {"type": "Polygon", "coordinates": [[
            [config.PRECINCT_ORIGIN_LONLAT[0], config.PRECINCT_ORIGIN_LONLAT[1]],
            [config.PRECINCT_ORIGIN_LONLAT[0] + 0.0001, config.PRECINCT_ORIGIN_LONLAT[1]],
            [config.PRECINCT_ORIGIN_LONLAT[0] + 0.0001, config.PRECINCT_ORIGIN_LONLAT[1] + 0.0001],
            [config.PRECINCT_ORIGIN_LONLAT[0], config.PRECINCT_ORIGIN_LONLAT[1] + 0.0001],
            [config.PRECINCT_ORIGIN_LONLAT[0], config.PRECINCT_ORIGIN_LONLAT[1]],
        ]]},
    }
    # road running north-south, ~100m west of the unit
    road_lon = config.PRECINCT_ORIGIN_LONLAT[0] - 0.0011
    roads = {"features": [{
        "properties": {"highway": "tertiary", "name": "Test Road"},
        "geometry": {"type": "LineString", "coordinates": [
            [road_lon, config.PRECINCT_ORIGIN_LONLAT[1] - 0.001],
            [road_lon, config.PRECINCT_ORIGIN_LONLAT[1] + 0.001],
        ]},
    }]}

    unblocked = noise.hourly_db_for_unit(unit, roads, {"features": [unit]})

    # a tall blocker building sitting directly between the road and the unit
    blocker_lon = config.PRECINCT_ORIGIN_LONLAT[0] - 0.0005
    blocker = {
        "properties": {"unit_id": "BLOCKER"},
        "geometry": {"type": "Polygon", "coordinates": [[
            [blocker_lon - 0.00005, config.PRECINCT_ORIGIN_LONLAT[1] - 0.0002],
            [blocker_lon + 0.00005, config.PRECINCT_ORIGIN_LONLAT[1] - 0.0002],
            [blocker_lon + 0.00005, config.PRECINCT_ORIGIN_LONLAT[1] + 0.0002],
            [blocker_lon - 0.00005, config.PRECINCT_ORIGIN_LONLAT[1] + 0.0002],
            [blocker_lon - 0.00005, config.PRECINCT_ORIGIN_LONLAT[1] - 0.0002],
        ]]},
    }
    blocked = noise.hourly_db_for_unit(unit, roads, {"features": [unit, blocker]})

    assert blocked["hourly_db"]["14"] < unblocked["hourly_db"]["14"]
    assert unblocked["hourly_db"]["14"] - blocked["hourly_db"]["14"] == pytest.approx(config.BARRIER_ATTENUATION_DB, abs=0.1)
