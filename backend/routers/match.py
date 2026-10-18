from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import scoring

router = APIRouter(prefix="/match", tags=["match"])


class MatchRequest(BaseModel):
    description: str


@router.post("")
def match_units(req: MatchRequest):
    try:
        return scoring.match(req.description)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
