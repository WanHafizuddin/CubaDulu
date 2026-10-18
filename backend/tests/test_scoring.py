from services import scoring


def unit(unit_id, price_rm, heat, noise, school_walk_min=None, kl_sentral_am=None):
    u = {
        "unit_id": unit_id,
        "price_rm": price_rm,
        "sun": {"heat_rating": heat},
        "noise": {"rating": noise},
        "commute": {"destinations": {}},
        "amenities": {},
    }
    if school_walk_min is not None:
        u["amenities"]["school"] = {"name": "Test School", "walk_min": school_walk_min}
    if kl_sentral_am is not None:
        u["commute"]["destinations"]["KL Sentral"] = {"am_min": kl_sentral_am, "pm_min": kl_sentral_am}
    return u


def test_normalize_higher_is_better():
    assert scoring._normalize([10, 20, 30], higher_is_better=True) == [0.0, 0.5, 1.0]


def test_normalize_lower_is_better():
    assert scoring._normalize([10, 20, 30], higher_is_better=False) == [1.0, 0.5, 0.0]


def test_normalize_flat_list_scores_everyone_full_marks():
    assert scoring._normalize([5, 5, 5], higher_is_better=True) == [1.0, 1.0, 1.0]


def test_match_filters_by_budget(monkeypatch):
    units = [
        unit("A", price_rm=500_000, heat="Low", noise="Quiet"),
        unit("B", price_rm=900_000, heat="Low", noise="Quiet"),
    ]
    monkeypatch.setattr(scoring, "_load_units", lambda: units)
    monkeypatch.setattr(
        scoring.gemini,
        "extract_weights",
        lambda desc: {
            "heat_sensitivity": 0.5, "noise_sensitivity": 0.5, "commute_importance": 0.5,
            "commute_destinations": [], "school_importance": 0.5, "budget_max_rm": 600_000,
        },
    )
    seen = {}
    monkeypatch.setattr(scoring.gemini, "explain_top_units", lambda top, desc: seen.setdefault("top", top) or [])

    scoring.match("I need somewhere affordable")
    assert [u["unit_id"] for u in seen["top"]] == ["A"]


def test_match_returns_empty_when_budget_excludes_everyone(monkeypatch):
    units = [unit("A", price_rm=900_000, heat="Low", noise="Quiet")]
    monkeypatch.setattr(scoring, "_load_units", lambda: units)
    monkeypatch.setattr(
        scoring.gemini,
        "extract_weights",
        lambda desc: {
            "heat_sensitivity": 0.5, "noise_sensitivity": 0.5, "commute_importance": 0.5,
            "commute_destinations": [], "school_importance": 0.5, "budget_max_rm": 100_000,
        },
    )
    result = scoring.match("too cheap to match anything")
    assert result["results"] == []


def test_match_ranks_cooler_quieter_unit_first_when_sensitive(monkeypatch):
    units = [
        unit("HOT", price_rm=600_000, heat="High", noise="Noisy"),
        unit("COOL", price_rm=600_000, heat="Low", noise="Quiet"),
    ]
    monkeypatch.setattr(scoring, "_load_units", lambda: units)
    monkeypatch.setattr(
        scoring.gemini,
        "extract_weights",
        lambda desc: {
            "heat_sensitivity": 1.0, "noise_sensitivity": 1.0, "commute_importance": 0.0,
            "commute_destinations": [], "school_importance": 0.0, "budget_max_rm": None,
        },
    )
    seen = {}
    monkeypatch.setattr(scoring.gemini, "explain_top_units", lambda top, desc: seen.setdefault("top", top) or [])

    scoring.match("I hate heat and noise")
    assert [u["unit_id"] for u in seen["top"]] == ["COOL", "HOT"]


def test_match_handles_missing_commute_destination_without_crashing(monkeypatch):
    units = [unit("A", price_rm=600_000, heat="Low", noise="Quiet")]  # no KL Sentral commute data
    monkeypatch.setattr(scoring, "_load_units", lambda: units)
    monkeypatch.setattr(
        scoring.gemini,
        "extract_weights",
        lambda desc: {
            "heat_sensitivity": 0.5, "noise_sensitivity": 0.5, "commute_importance": 0.8,
            "commute_destinations": ["KL Sentral"], "school_importance": 0.5, "budget_max_rm": None,
        },
    )
    monkeypatch.setattr(scoring.gemini, "explain_top_units", lambda top, desc: [])

    result = scoring.match("I commute to KL Sentral")
    assert result["weights"]["commute_destinations"] == ["KL Sentral"]
