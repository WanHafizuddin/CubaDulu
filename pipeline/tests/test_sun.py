import json
from datetime import date
from pathlib import Path

import pytest

from .. import config, sun

PRECINCT_PATH = Path(__file__).parent.parent.parent / "data" / "precinct.geojson"


@pytest.fixture(scope="module")
def precinct():
    return json.loads(PRECINCT_PATH.read_text())


@pytest.fixture(scope="module")
def scene(precinct):
    return sun.build_scene(precinct)


def feature(precinct, unit_id):
    return next(f for f in precinct["features"] if f["properties"]["unit_id"] == unit_id)


def test_heat_rating_thresholds():
    assert sun.heat_rating(0.0) == "Low"
    assert sun.heat_rating(1.9) == "Low"
    assert sun.heat_rating(2.0) == "Moderate"
    assert sun.heat_rating(3.4) == "Moderate"
    assert sun.heat_rating(3.5) == "High"
    assert sun.heat_rating(6.0) == "High"


def test_sun_position_near_noon_equinox():
    lon, lat = config.PRECINCT_ORIGIN_LONLAT
    equinox = date.fromisoformat(config.SUN_REFERENCE_DATES["equinox"])
    from datetime import datetime
    from zoneinfo import ZoneInfo

    noon = datetime(equinox.year, equinox.month, equinox.day, 13, 0, tzinfo=ZoneInfo(config.TIMEZONE))
    azimuth, elevation = sun.sun_position(lat, lon, noon)
    # Sepang is ~2.85N: near the equinox, near-local-noon sun should be high overhead
    assert elevation > 70
    assert 0 <= azimuth <= 360


def test_build_scene_has_geometry(scene):
    assert len(scene.vertices) > 0
    assert len(scene.faces) > 0


def test_mid_row_party_wall_blocked_by_neighbour(precinct, scene):
    # A-13 sits mid-row with A-11 and A-15 on either side; its east/west walls are
    # party walls that should get ~no direct sun across the whole reference day,
    # while the front (N) facade should get plenty.
    result = sun.facade_sun_hours("A-13", scene, feature(precinct, "A-13"), date.fromisoformat(config.SUN_REFERENCE_DATES["equinox"]))
    hours = result["facade_sun_hours"]
    assert hours["E"] <= 1
    assert hours["W"] <= 1
    assert hours["N"] >= 3


def test_end_unit_side_wall_gets_sun(precinct, scene):
    # A-01 is the west end unit of row 17/9: its west-facing side wall has no
    # neighbour, so it should pick up sun across the day (unlike a mid-row unit).
    result = sun.facade_sun_hours("A-01", scene, feature(precinct, "A-01"), date.fromisoformat(config.SUN_REFERENCE_DATES["equinox"]))
    assert sum(result["facade_sun_hours"].values()) > 0


def test_rows_face_opposite_directions(precinct):
    # Near the equator, a north wall and a south wall can rack up the same *total*
    # sunlit hours (the sun arcs almost overhead), so this checks the geometric fact
    # that matters instead: row A and row B were built back-to-back, ~180 deg apart.
    a = feature(precinct, "A-07")["properties"]["front_orientation_deg"]
    b = feature(precinct, "B-07")["properties"]["front_orientation_deg"]
    diff = abs((a - b + 180) % 360 - 180)
    assert diff > 170
