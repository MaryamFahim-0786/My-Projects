from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SummarizeRequest,
    SummarizeResponse,
)
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/api", tags=["ai"])


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(req: SummarizeRequest):
    try:
        result = await gemini_service.summarize_article(req.title, req.content)
        return SummarizeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Summarization failed: {e}")


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        reply = await gemini_service.chat(req.message, req.history, req.article_context)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Chat failed: {e}")
