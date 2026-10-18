from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services import gemini

router = APIRouter(prefix="/units", tags=["chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []


@router.post("/{unit_id}/chat")
def chat_with_unit(unit_id: str, req: ChatRequest):
    history = [m.model_dump() for m in req.history]
    try:
        return gemini.ask_the_unit(unit_id, req.message, history)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
