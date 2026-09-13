import hashlib
from typing import List, Optional

import httpx

from app.config import settings
from app.models.schemas import Article


class NewsService:
    """Thin wrapper around NewsAPI.org's top-headlines and everything endpoints."""

    def __init__(self):
        self.base_url = settings.NEWS_API_BASE_URL
        self.api_key = settings.NEWS_API_KEY

    @staticmethod
    def _make_id(url: str) -> str:
        return hashlib.md5(url.encode("utf-8")).hexdigest()[:12]

    def _parse_article(self, raw: dict) -> Article:
        return Article(
            id=self._make_id(raw.get("url", "")),
            title=raw.get("title") or "Untitled",
            description=raw.get("description"),
            content=raw.get("content") or raw.get("description") or "",
            url=raw.get("url", ""),
            image_url=raw.get("urlToImage"),
            source=(raw.get("source") or {}).get("name", "Unknown"),
            published_at=raw.get("publishedAt"),
        )

    def _clean(self, raw_articles: List[dict]) -> List[Article]:
        return [
            self._parse_article(a)
            for a in raw_articles
            if a.get("title") and a.get("title") != "[Removed]"
        ]

    async def get_top_headlines(
        self,
        category: Optional[str] = None,
        country: str = "us",
        page_size: int = 20,
    ) -> List[Article]:
        if not self.api_key:
            raise ValueError("NEWS_API_KEY is not configured on the server")

        params = {"apiKey": self.api_key, "country": country, "pageSize": page_size}
        if category and category != "general":
            params["category"] = category

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{self.base_url}/top-headlines", params=params)
            resp.raise_for_status()
            data = resp.json()

        return self._clean(data.get("articles", []))

    async def search_news(
        self,
        query: str,
        page_size: int = 20,
        sort_by: str = "publishedAt",
    ) -> List[Article]:
        if not self.api_key:
            raise ValueError("NEWS_API_KEY is not configured on the server")

        params = {
            "apiKey": self.api_key,
            "q": query,
            "pageSize": page_size,
            "sortBy": sort_by,
            "language": "en",
        }

        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{self.base_url}/everything", params=params)
            resp.raise_for_status()
            data = resp.json()

        return self._clean(data.get("articles", []))


news_service = NewsService()
