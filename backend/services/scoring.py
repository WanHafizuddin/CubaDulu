"""Normalise unit factors 0-1, apply user weights, filter by budget."""
import json
from pathlib import Path

from . import gemini

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "units_livability.json"

_HEAT_SCORE = {"Low": 1.0, "Moderate": 0.5, "High": 0.0}
_NOISE_SCORE = {"Quiet": 1.0, "Moderate": 0.5, "Noisy": 0.0}
_DEFAULT_WEIGHT = 0.5
_MISSING_SCHOOL_WALK_MIN = 999  # units with no school in range rank last, not crash


def _load_units() -> list[dict]:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def _normalize(values: list[float], higher_is_better: bool) -> list[float]:
    """Min-max normalise to 0-1. A flat list (all equal) scores everyone 1.0 -
    the factor genuinely doesn't distinguish these units, so it shouldn't penalise any."""
    lo, hi = min(values), max(values)
    if hi == lo:
        return [1.0] * len(values)
    if higher_is_better:
        return [(v - lo) / (hi - lo) for v in values]
    return [(hi - v) / (hi - lo) for v in values]


def _commute_minutes(unit: dict, destinations: list[str]) -> float:
    available = [
        unit["commute"]["destinations"][d]["am_min"]
        for d in destinations
        if d in unit["commute"]["destinations"]
    ]
    return sum(available) / len(available) if available else 0.0


def match(description: str) -> dict:
    weights = gemini.extract_weights(description)
    units = _load_units()

    budget = weights.get("budget_max_rm")
    if budget:
        units = [u for u in units if u["price_rm"] <= budget]
    if not units:
        return {"weights": weights, "results": []}

    heat_scores = [_HEAT_SCORE.get(u["sun"]["heat_rating"], 0.5) for u in units]
    noise_scores = [_NOISE_SCORE.get(u["noise"]["rating"], 0.5) for u in units]

    destinations = weights.get("commute_destinations") or []
    if destinations and any(d in u["commute"]["destinations"] for u in units for d in destinations):
        commute_minutes = [_commute_minutes(u, destinations) for u in units]
        commute_scores = _normalize(commute_minutes, higher_is_better=False)
    else:
        commute_scores = [_DEFAULT_WEIGHT] * len(units)

    school_walk = [u["amenities"].get("school", {}).get("walk_min", _MISSING_SCHOOL_WALK_MIN) for u in units]
    school_scores = _normalize(school_walk, higher_is_better=False)

    scored = []
    for i, unit in enumerate(units):
        score = (
            weights.get("heat_sensitivity", _DEFAULT_WEIGHT) * heat_scores[i]
            + weights.get("noise_sensitivity", _DEFAULT_WEIGHT) * noise_scores[i]
            + weights.get("commute_importance", _DEFAULT_WEIGHT) * commute_scores[i]
            + weights.get("school_importance", _DEFAULT_WEIGHT) * school_scores[i]
        )
        scored.append((score, unit))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    top_units = [unit for _, unit in scored[:3]]

    explanations = gemini.explain_top_units(top_units, description)
    return {"weights": weights, "results": explanations}
