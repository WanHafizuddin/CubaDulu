from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/commute", tags=["commute"])


class CustomCommuteRequest(BaseModel):
    destination: str


@router.post("/custom")
def custom_commute(req: CustomCommuteRequest):
    # TODO: call Google Routes once for the precinct centroid, cache result
    return {"destination": req.destination, "am_min": None, "pm_min": None}
