from typing import List, Optional

import google.generativeai as genai

from app.config import settings
from app.models.schemas import ChatMessage

genai.configure(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = (
    "You are the AI news assistant inside 'Maryam's News', a news reading app. "
    "You help readers understand current events: summarizing articles, answering "
    "questions about the news, and giving balanced, factual context. Keep answers "
    "concise and conversational, mention the outlet by name when it matters, and "
    "say plainly when a fast-moving story might have developed since your last "
    "information instead of guessing."
)


class GeminiService:
    def __init__(self):
        self.model_name = settings.GEMINI_MODEL

    def _get_model(self, system_instruction: Optional[str] = None):
        return genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=system_instruction or SYSTEM_PROMPT,
        )

    async def summarize_article(self, title: str, content: str) -> dict:
        model = self._get_model()
        prompt = (
            "Summarize this news article in 2-3 sentences, then list 3-5 key points.\n\n"
            f"Title: {title}\n\n"
            f"Content: {content}\n\n"
            "Respond in exactly this format, no extra commentary:\n"
            "SUMMARY: <2-3 sentence summary>\n"
            "POINTS:\n- point 1\n- point 2\n- point 3"
        )
        response = model.generate_content(prompt)
        return self._parse_summary(response.text or "")

    @staticmethod
    def _parse_summary(text: str) -> dict:
        summary = ""
        points: List[str] = []

        if "SUMMARY:" in text:
            after = text.split("SUMMARY:", 1)[1]
            if "POINTS:" in after:
                summary_part, points_part = after.split("POINTS:", 1)
                summary = summary_part.strip()
                for line in points_part.strip().splitlines():
                    cleaned = line.strip().lstrip("-•*").strip()
                    if cleaned:
                        points.append(cleaned)
            else:
                summary = after.strip()
        else:
            summary = text.strip()

        return {"summary": summary, "key_points": points}

    async def chat(
        self,
        message: str,
        history: Optional[List[ChatMessage]] = None,
        article_context: Optional[str] = None,
    ) -> str:
        system = SYSTEM_PROMPT
        if article_context:
            system += f"\n\nThe reader currently has this article open:\n{article_context}"

        model = self._get_model(system_instruction=system)

        gemini_history = []
        for msg in history or []:
            role = "user" if msg.role == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg.content]})

        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(message)
        return response.text or ""


gemini_service = GeminiService()
