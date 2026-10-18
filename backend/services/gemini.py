"""Gemini calls: life-fit weight extraction, top-3 explanations, ask-the-unit chat."""
import json
import os

import google.generativeai as genai

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

_MODEL = "gemini-2.0-flash"


def extract_weights(description: str) -> dict:
    """Free-text life description -> strict JSON scoring weights."""
    # TODO: prompt Gemini for heat_sensitivity, noise_sensitivity, commute_importance,
    # commute_destinations, school_importance, flood_concern, budget_max_rm (0-1 each)
    raise NotImplementedError


def explain_top_units(units: list[dict], description: str) -> list[dict]:
    """Top-3 units' data + user text -> short explanation per unit, numbers-only."""
    # TODO
    raise NotImplementedError


def ask_the_unit(unit_id: str, message: str, history: list) -> dict:
    """Answer grounded only in this unit's livability record. No invented numbers."""
    # TODO: load data/processed/units_livability.json record for unit_id,
    # build system prompt from it, call Gemini
    raise NotImplementedError
