from .. import commute


def test_commute_for_precinct_caches_and_never_recalls_route_minutes(tmp_path, monkeypatch):
    monkeypatch.setattr(commute, "CACHE_PATH", tmp_path / "commute_cache.json")
    calls = []

    def fake_route_minutes(origin, destination, departure):
        calls.append((origin, destination, departure))
        return 42.0

    monkeypatch.setattr(commute, "route_minutes", fake_route_minutes)

    centroid = (2.8443, 101.70285)
    first = commute.commute_for_precinct(centroid)
    assert set(first.keys()) == set(commute.DEFAULT_DESTINATION_COORDS.keys())
    assert all(v["am_min"] == 42.0 and v["pm_min"] == 42.0 for v in first.values())
    calls_after_first = len(calls)
    assert calls_after_first == len(commute.DEFAULT_DESTINATION_COORDS) * 2  # am + pm each

    second = commute.commute_for_precinct(centroid)
    assert second == first
    assert len(calls) == calls_after_first  # cache hit, no new calls


def test_commute_for_precinct_persists_to_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(commute, "CACHE_PATH", tmp_path / "commute_cache.json")
    monkeypatch.setattr(commute, "route_minutes", lambda o, d, dep: 10.0)

    commute.commute_for_precinct((2.8443, 101.70285))
    assert (tmp_path / "commute_cache.json").exists()


def test_custom_destination_geocodes_once_then_caches(tmp_path, monkeypatch):
    monkeypatch.setattr(commute, "CACHE_PATH", tmp_path / "commute_cache.json")
    geocode_calls = []
    route_calls = []

    monkeypatch.setattr(commute, "geocode", lambda place: (geocode_calls.append(place), (3.0, 101.5))[1])
    monkeypatch.setattr(commute, "route_minutes", lambda o, d, dep: (route_calls.append(1), 15.0)[1])

    centroid = (2.8443, 101.70285)
    first = commute.commute_to_custom_destination(centroid, "Bangsar South")
    assert first == {"am_min": 15.0, "pm_min": 15.0}
    assert geocode_calls == ["Bangsar South"]
    assert len(route_calls) == 2

    second = commute.commute_to_custom_destination(centroid, "Bangsar South")
    assert second == first
    assert geocode_calls == ["Bangsar South"]  # not geocoded again
    assert len(route_calls) == 2  # not re-routed either


def test_custom_destination_is_scoped_per_precinct_key(tmp_path, monkeypatch):
    monkeypatch.setattr(commute, "CACHE_PATH", tmp_path / "commute_cache.json")
    monkeypatch.setattr(commute, "geocode", lambda place: (3.0, 101.5))
    monkeypatch.setattr(commute, "route_minutes", lambda o, d, dep: 20.0)

    commute.commute_for_precinct((2.8443, 101.70285))
    result = commute.commute_to_custom_destination((2.8443, 101.70285), "Mid Valley")
    cache = commute._load_cache()
    key = "2.84430,101.70285"
    assert "destinations" in cache[key]
    assert "Mid Valley" in cache[key]["custom"]
    assert result == {"am_min": 20.0, "pm_min": 20.0}
