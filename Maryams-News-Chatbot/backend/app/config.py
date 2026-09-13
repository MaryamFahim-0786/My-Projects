import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Central place for all environment-driven configuration."""

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

    _raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")
    ALLOWED_ORIGINS: list = [o.strip() for o in _raw_origins.split(",") if o.strip()]


settings = Settings()
