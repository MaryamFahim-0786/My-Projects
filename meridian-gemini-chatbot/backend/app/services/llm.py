from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from app.core.config import settings


@lru_cache
def get_chat_model(streaming: bool = False) -> ChatGoogleGenerativeAI:
    """Returns a cached Gemini chat model instance."""
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.4,
        streaming=streaming,
        convert_system_message_to_human=True,
    )


@lru_cache
def get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    """Returns a cached Gemini embeddings model (768-dim, matches DocumentChunk.embedding)."""
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GOOGLE_API_KEY,
       
    )