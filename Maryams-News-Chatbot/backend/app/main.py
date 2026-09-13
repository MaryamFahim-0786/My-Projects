from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import chat, news

app = FastAPI(
    title="Maryam's News API",
    description="Backend for Maryam's News — live headlines plus a Gemini-powered AI reading assistant.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(news.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    return {"status": "ok", "service": "Maryam's News API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
