import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ---- Auth ----
class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Chat ----
class ChatRequest(BaseModel):
    conversation_id: uuid.UUID | None = None
    message: str
    use_rag: bool = True
    use_tools: bool = True


class MessageOut(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Documents ----
class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    created_at: datetime

    class Config:
        from_attributes = True
