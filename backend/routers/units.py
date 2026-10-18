import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/units", tags=["units"])

DATA_PATH = Path(__file__).parent.parent.parent / "data" / "processed" / "units_livability.json"


def _load_units() -> list[dict]:
    if not DATA_PATH.exists():
        return []
    return json.loads(DATA_PATH.read_text())


@router.get("")
def list_units():
    return _load_units()


@router.get("/compare")
def compare_units(ids: str):
    wanted = {i.strip() for i in ids.split(",") if i.strip()}
    units = [u for u in _load_units() if u["unit_id"] in wanted]
    return {"units": units}


@router.get("/{unit_id}")
def get_unit(unit_id: str):
    for unit in _load_units():
        if unit["unit_id"] == unit_id:
            return unit
    raise HTTPException(status_code=404, detail="unit not found")
