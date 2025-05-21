from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    user_id: int
    message: str


class AnonymousChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    type: str  # "text", "function", "error"
    content: Optional[str] = None
    function_name: Optional[str] = None
    result: Optional[str] = None
    error: Optional[str] = None


class InitiateChatResponse(BaseModel):
    user_id: int
    user_name: Optional[str] = None
    is_anonymous: bool
    welcome_message: str
    new_session: bool
