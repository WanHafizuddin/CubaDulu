from fastapi import APIRouter
from pydantic import BaseModel

from services import scoring

router = APIRouter(prefix="/match", tags=["match"])


class MatchRequest(BaseModel):
    description: str


@router.post("")
def match_units(req: MatchRequest):
    return scoring.match(req.description)
