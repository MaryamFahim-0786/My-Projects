import json
import logging
from typing import AsyncGenerator

from langchain.prompts import ChatPromptTemplate

from app.core.config import settings
from app.services.contact_service import send_email_tool
from app.services.llm_factory import get_chat_llm
from app.services.rag_service import get_retriever, is_retriever_ready

logger = logging.getLogger(__name__)


AGENT_SYSTEM_PROMPT = f"""You are the AI digital twin of **{settings.PORTFOLIO_OWNER}**.
You speak in the **FIRST PERSON** ("I", "me", "my") as if you ARE {settings.PORTFOLIO_OWNER}.
Your goal is to have a natural, friendly conversation with visitors to your portfolio.

**CRITICAL IDENTITY RULES:**
1. ALWAYS speak in first person.
2. Never claim to be someone other than Maryam Fahim.
3. Do not mention internal retrieval, databases, tools, or system implementation.
4. When a visitor talks about Maryam in third person, answer in first person.

**ANTI-HALLUCINATION & FACTUALITY:**
1. Specific facts about education, internship, projects and experience must come from the supplied portfolio context.
2. Never invent employers, job titles, responsibilities, technologies, achievements or experience.
3. Never claim years of full-time industry experience.
4. Never mix details between different projects.
5. If the supplied context does not contain a specific fact, say:
   "I don't have that specific detail handy, but I can tell you about a related part of my work."

**PROJECT BOUNDARIES:**
- Meridian = Next.js 14 + FastAPI + LangChain + Gemini + PostgreSQL/pgvector + JWT auth, with per-user RAG and agent tools.
- Simple RAG Chatbot = FastAPI + Gemini + PostgreSQL/pgvector, without LangChain.
- RAG Chatbot (CLI) = Python + LangChain + ChromaDB + OpenAI.
- AI Weather Platform = FastAPI + LangGraph agent + Groq + Open-Meteo + Next.js.
- Crypto AI Assistant = Flask + LangChain agent + CoinGecko + Next.js dashboard + Electron wrapper.
- Mary's News = FastAPI + Gemini + NewsAPI + React/Vite.
- Bank Management System = Python + SQLite, CLI and Tkinter GUI.
- Car Rental System = Python + SQLite + Tkinter GUI.
- Library Management System = Python + SQLite CLI.
- Portfolio = customized from an open-source MIT template by Roy Amit.

**PHONE NUMBER:**
Never write out a phone number.
For WhatsApp, use:
https://wa.me/923340079140

**TOPIC GUARDRAILS:**
Your purpose is to discuss Maryam Fahim, her projects, skills, education and professional background.

For unrelated questions such as general trivia, sports, creative writing, cooking or unrelated coding tutorials, politely decline and pivot back to the portfolio.

**LANGUAGE:**
Reply in the language used by the visitor.
If they use Urdu or Roman Urdu, you may reply in Roman Urdu.
Otherwise use English.

**RESPONSE STYLE:**
- Professional
- Warm
- Honest
- Conversational
- Concise
- Use bullets when useful
- Do not exaggerate
- Do not invent information

**IMPORTANT:**
Use ONLY the supplied portfolio context for specific portfolio facts.
"""


async def rag_tool_wrapper(question: str) -> str:
    """Retrieves portfolio information using the BM25 retriever."""

    if not is_retriever_ready():
        return (
            "I am currently waking up and loading my portfolio information. "
            "Please ask me again in a few seconds."
        )

    try:
        retriever = get_retriever()
        docs = await retriever.ainvoke(question)

        if not docs:
            return "No relevant portfolio information was found."

        return "\n\n".join(
            doc.page_content
            for doc in docs
        )

    except Exception as e:
        logger.error(
            f"RAG retrieval error: {e}",
            exc_info=True
        )
        return "I could not retrieve the relevant portfolio information."


async def send_resume_email(recipient: str) -> str:
    """Sends the resume email via the configured mail service."""

    subject = f"{settings.PORTFOLIO_OWNER}'s Resume"

    body = f"""
        <p>Hello,</p>

        <p>
            Thank you for your interest in
            {settings.PORTFOLIO_OWNER}'s profile.
        </p>

        <p>
            You can view and download the resume here:
        </p>

        <p>
            <a href="{settings.RESUME_LINK}"
               style="background-color:#4F46E5;
                      color:white;
                      padding:12px 24px;
                      text-decoration:none;
                      border-radius:6px;
                      font-weight:bold;
                      display:inline-block;">
                View Resume PDF
            </a>
        </p>

        <br>

        <p>Best regards,</p>
        <p>{settings.PORTFOLIO_OWNER}'s AI Assistant</p>
    """

    try:
        send_email_tool(
            recipient=recipient,
            subject=subject,
            body=body
        )

        logger.info(
            f"Resume sent to {recipient}"
        )

        return f"Successfully sent email to {recipient}."

    except Exception as e:
        logger.error(
            f"Email Tool Error: {e}",
            exc_info=True
        )

        return f"Error sending email: {str(e)}"


# ------------------------------------------------------------------
# Gemini + BM25 RAG
# ------------------------------------------------------------------

llm = get_chat_llm()

rag_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        AGENT_SYSTEM_PROMPT
        + """

The following information was retrieved from Maryam's portfolio.

PORTFOLIO CONTEXT:
{context}

Use this context to answer the visitor.

If the context does not contain enough information:
- Do not guess.
- Be honest.
- Offer a related topic that you can discuss.

Never mention the words:
- knowledge base
- database
- retrieval
- internal context
- tool
- tool calling
"""
    ),
    (
        "human",
        "{input}"
    ),
])


async def generate_rag_response(
    message: str,
    session_id: str
) -> str:
    """Generate a grounded Gemini response using BM25 retrieval."""

    if not is_retriever_ready():
        return (
            "I am still loading my portfolio information. "
            "Please try again in a few seconds."
        )

    try:
        # Retrieve relevant portfolio chunks
        retriever = get_retriever()
        docs = await retriever.ainvoke(message)

        if docs:
            context = "\n\n".join(
                doc.page_content
                for doc in docs
            )
        else:
            context = (
                "No relevant portfolio information was found."
            )

        # Generate response without Redis history
        chain = rag_prompt | llm

        response = await chain.ainvoke({
            "input": message,
            "context": context,
        })

        answer = _chunk_text(
            getattr(response, "content", "")
        )

        if not answer:
            answer = (
                "I couldn't generate a response right now. "
                "Please try again."
            )

        return answer

    except Exception as e:
        logger.error(
            f"RAG response error: {e}",
            exc_info=True
        )

        raise


def _chunk_text(content) -> str:
    """
    Gemini/LangChain may return content as a string
    or a list of content parts.
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for part in content:
            if isinstance(part, str):
                parts.append(part)

            elif isinstance(part, dict):
                text = part.get("text", "")

                if text:
                    parts.append(text)

        return "".join(parts)

    return ""


def format_sse_event(
    event_type: str,
    data: dict
) -> str:
    """Formats an SSE event."""

    return (
        f"event: {event_type}\n"
        f"data: {json.dumps(data)}\n\n"
    )


async def stream_agent_response(
    message: str,
    session_id: str
) -> AsyncGenerator[str, None]:
    """
    Generates the chatbot response.

    Uses BM25 retrieval + Gemini.
    Redis conversation history is intentionally disabled
    for serverless/Vercel compatibility.
    """

    try:
        yield format_sse_event(
            "status",
            {
                "message": "Searching portfolio..."
            }
        )

        # Check retriever
        if not is_retriever_ready():
            yield format_sse_event(
                "error",
                {
                    "message": (
                        "Portfolio information is still loading. "
                        "Please try again shortly."
                    )
                }
            )
            return

        # Retrieve relevant portfolio documents
        retriever = get_retriever()

        docs = await retriever.ainvoke(message)

        if docs:
            context = "\n\n".join(
                doc.page_content
                for doc in docs
            )
        else:
            context = (
                "No relevant portfolio information was found."
            )

        yield format_sse_event(
            "status",
            {
                "message": "Generating response..."
            }
        )

        # Gemini chain
        chain = rag_prompt | llm

        response = await chain.ainvoke({
            "input": message,
            "context": context,
        })

        answer = _chunk_text(
            getattr(response, "content", "")
        )

        if not answer:
            answer = (
                "I couldn't generate a response right now. "
                "Please try again."
            )

        # Send response
        yield format_sse_event(
            "token",
            {
                "content": answer
            }
        )

    except Exception as e:
        logger.error(
            f"Stream Agent Error: {e}",
            exc_info=True
        )

        yield format_sse_event(
            "error",
            {
                "message": (
                    "Sorry, an unexpected system error occurred."
                )
            }
        )

    finally:
        yield format_sse_event(
            "done",
            {
                "message": "[DONE]"
            }
        )