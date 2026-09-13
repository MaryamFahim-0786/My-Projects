from typing import List, Optional
from pydantic import BaseModel


class Article(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source: str
    published_at: Optional[str] = None


class NewsResponse(BaseModel):
    articles: List[Article]
    total_results: int


class SummarizeRequest(BaseModel):
    title: str
    content: str


class SummarizeResponse(BaseModel):
    summary: str
    key_points: List[str]


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    article_context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
