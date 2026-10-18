"""Gemini calls: life-fit weight extraction, top-3 explanations, ask-the-unit chat."""
import json
import os
from pathlib import Path

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

_MODEL = "gemini-2.5-flash"
_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "units_livability.json"

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set (see backend/.env.example)")
        _client = genai.Client(api_key=api_key)
    return _client


class LifeFitWeights(BaseModel):
    heat_sensitivity: float = Field(ge=0, le=1, description="0 = doesn't care about heat/sun, 1 = very heat-averse")
    noise_sensitivity: float = Field(ge=0, le=1, description="0 = doesn't care about noise, 1 = needs quiet")
    commute_importance: float = Field(ge=0, le=1, description="0 = commute doesn't matter, 1 = commute is critical")
    commute_destinations: list[str] = Field(description="Named destinations the buyer commutes to or cares about")
    school_importance: float = Field(ge=0, le=1, description="0 = no kids/doesn't matter, 1 = school proximity is critical")
    budget_max_rm: float | None = Field(default=None, description="Max budget in Ringgit if stated, else null")


class UnitExplanation(BaseModel):
    unit_id: str
    explanation: str


def extract_weights(description: str) -> dict:
    """Free-text life description -> strict JSON scoring weights."""
    client = _get_client()
    prompt = (
        "A home buyer described their life like this:\n\n"
        f'"""{description}"""\n\n'
        "Extract scoring weights for matching them to a housing unit in a Malaysian "
        "township precinct. Available named commute destinations are KL Sentral, "
        "Putrajaya, KLIA, Cyberjaya and UPM - list any of those (or other places) the "
        "buyer mentions commuting to or caring about in commute_destinations."
    )
    response = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=LifeFitWeights,
        ),
    )
    return response.parsed.model_dump()


def explain_top_units(units: list[dict], description: str) -> list[dict]:
    """Top-3 units' data + user text -> short explanation per unit, numbers-only."""
    client = _get_client()
    prompt = (
        "A home buyer described their life like this:\n\n"
        f'"""{description}"""\n\n'
        "Here are their top 3 matched units (JSON livability records):\n\n"
        f"{json.dumps(units, indent=2)}\n\n"
        "For each unit, write a 2-3 sentence explanation of why it fits this buyer. "
        "Cite ONLY numbers that appear in the JSON above - never invent a figure. "
        "Return them in the same order as the input units."
    )
    response = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=list[UnitExplanation],
        ),
    )
    return [item.model_dump() for item in response.parsed]


def ask_the_unit(unit_id: str, message: str, history: list) -> dict:
    """Answer grounded only in this unit's livability record. No invented numbers."""
    client = _get_client()
    units = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    unit = next((u for u in units if u["unit_id"] == unit_id), None)
    if unit is None:
        return {"answer": f"Unit {unit_id} isn't in the dataset."}

    system_prompt = (
        "You answer questions about ONE specific housing unit, grounded ONLY in the "
        "data record below. If the question asks about something this data doesn't "
        "cover (e.g. interior finishes, exact move-in date), say plainly that it "
        "isn't in the data - never invent a number or fact.\n\n"
        f"Unit record:\n{json.dumps(unit, indent=2)}"
    )

    contents = [
        types.Content(role="user" if turn["role"] == "user" else "model", parts=[types.Part(text=turn["content"])])
        for turn in history
    ]
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    response = client.models.generate_content(
        model=_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )
    return {"answer": response.text}
