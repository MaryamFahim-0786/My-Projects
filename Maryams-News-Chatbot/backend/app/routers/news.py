from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import NewsResponse
from app.services.news_service import news_service

router = APIRouter(prefix="/api/news", tags=["news"])


@router.get("/top", response_model=NewsResponse)
async def get_top_headlines(
    category: Optional[str] = Query(None, description="business, technology, sports, health, science, entertainment"),
    country: str = Query("us"),
    page_size: int = Query(20, le=50),
):
    try:
        articles = await news_service.get_top_headlines(
            category=category, country=country, page_size=page_size
        )
        return NewsResponse(articles=articles, total_results=len(articles))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch news: {e}")


@router.get("/search", response_model=NewsResponse)
async def search_news(
    q: str = Query(..., min_length=1),
    page_size: int = Query(20, le=50),
):
    try:
        articles = await news_service.search_news(query=q, page_size=page_size)
        return NewsResponse(articles=articles, total_results=len(articles))
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to search news: {e}")
