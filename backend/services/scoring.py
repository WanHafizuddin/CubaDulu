"""Normalise unit factors 0-1, apply user weights, filter by budget."""
from . import gemini


def match(description: str) -> dict:
    weights = gemini.extract_weights(description)
    # TODO: load data/processed/units_livability.json, normalise each factor
    # across units (higher = better), weighted-sum score, filter by budget_max_rm
    top_units: list[dict] = []
    explanations = gemini.explain_top_units(top_units, description)
    return {"weights": weights, "results": explanations}
