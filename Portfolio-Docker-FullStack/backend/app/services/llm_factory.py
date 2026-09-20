"""
Chooses the chat model and embedding model based on LLM_PROVIDER.

  LLM_PROVIDER="openai"  -> ChatOpenAI + OpenAIEmbeddings   (needs OPENAI_API_KEY, paid)
  LLM_PROVIDER="gemini"  -> ChatGoogleGenerativeAI + GoogleGenerativeAIEmbeddings
                            (needs GOOGLE_API_KEY, has a free tier)

Everything else in the app (agent, tools, RAG) is provider-independent.
"""
from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings


def get_chat_llm() -> BaseChatModel:
    if settings.LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=settings.GEMINI_MODEL,
            google_api_key=settings.GOOGLE_API_KEY.get_secret_value(),
            temperature=0,
            # Gemini 2.5 "thinking" tokens count towards this limit, so keep it generous.
            max_output_tokens=2048,
            convert_system_message_to_human=True,
        )

    from langchain_openai import ChatOpenAI

    return ChatOpenAI(
        api_key=settings.OPENAI_API_KEY.get_secret_value(),
        model=settings.OPENAI_MODEL,
        temperature=0,
        max_tokens=500,
    )


def get_embeddings() -> Embeddings:
    if settings.LLM_PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=settings.GEMINI_EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY.get_secret_value(),
        )

    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY.get_secret_value())
