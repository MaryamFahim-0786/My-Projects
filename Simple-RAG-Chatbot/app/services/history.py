from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatMessage


async def load_history(db: AsyncSession, session_id: str, limit: int = 20) -> list[dict]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    rows = list(reversed(result.scalars().all()))
    return [{"role": r.role, "content": r.content} for r in rows]


async def load_history_full(db: AsyncSession, session_id: str, limit: int = 100) -> list[ChatMessage]:
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def save_message(db: AsyncSession, session_id: str, role: str, content: str) -> None:
    db.add(ChatMessage(session_id=session_id, role=role, content=content))
    await db.commit()
