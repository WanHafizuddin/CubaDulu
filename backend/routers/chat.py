from fastapi import APIRouter
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
    return gemini.ask_the_unit(unit_id, req.message, req.history)
