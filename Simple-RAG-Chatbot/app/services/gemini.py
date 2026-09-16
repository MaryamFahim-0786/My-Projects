import google.generativeai as genai

from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

_chat_model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)


def embed_text(text: str, task_type: str = "retrieval_document") -> list[float]:
    """Embeds a single piece of text with Gemini, truncated/padded to EMBEDDING_DIM."""
    result = genai.embed_content(
        model=settings.GEMINI_EMBEDDING_MODEL,
        content=text,
        task_type=task_type,
        output_dimensionality=settings.EMBEDDING_DIM,
    )
    return result["embedding"]


def embed_batch(texts: list[str], task_type: str = "retrieval_document") -> list[list[float]]:
    return [embed_text(t, task_type=task_type) for t in texts]


def generate_answer(question: str, context_chunks: list[str], history: list[dict]) -> str:
    """Builds a grounded prompt from retrieved chunks + short chat history and asks Gemini."""
    if context_chunks:
        context_block = "\n\n".join(f"[Source {i + 1}] {c}" for i, c in enumerate(context_chunks))
        system_instruction = (
            "You are a helpful assistant that answers questions using the provided document "
            "excerpts. Cite sources like [Source 1] when you use them. If the excerpts don't "
            "contain the answer, say so plainly and answer from general knowledge instead.\n\n"
            f"Document excerpts:\n{context_block}"
        )
    else:
        system_instruction = (
            "You are a helpful assistant. No documents have been uploaded yet, so answer from "
            "general knowledge and mention that uploading a document would let you search it."
        )

    convo = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in history]

    model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL, system_instruction=system_instruction)
    chat = model.start_chat(history=convo)
    response = chat.send_message(question)
    return response.text
