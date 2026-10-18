from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/units", tags=["units"])


@router.get("")
def list_units():
    # TODO: load data/processed/units_livability.json
    return []


@router.get("/{unit_id}")
def get_unit(unit_id: str):
    # TODO: look up unit_id in units_livability.json
    raise HTTPException(status_code=404, detail="unit not found")


@router.get("/compare")
def compare_units(ids: str):
    # TODO: ids is a comma-separated list, e.g. "A-01,B-12"
    return {"units": []}
