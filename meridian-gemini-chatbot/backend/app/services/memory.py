import uuid

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Conversation, Message


async def get_or_create_conversation(
    db: AsyncSession, user_id: uuid.UUID, conversation_id: uuid.UUID | None
) -> Conversation:
    if conversation_id:
        result = await db.execute(
            select(Conversation).where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        conversation = result.scalar_one_or_none()
        if conversation:
            return conversation

    conversation = Conversation(user_id=user_id, title="New chat")
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def load_history(db: AsyncSession, conversation_id: uuid.UUID, limit: int = 20) -> list[BaseMessage]:
    """Loads the most recent messages for this conversation as LangChain message objects,
    giving the model short-term memory of the ongoing thread."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    rows = list(reversed(result.scalars().all()))

    history: list[BaseMessage] = []
    for row in rows:
        if row.role == "user":
            history.append(HumanMessage(content=row.content))
        elif row.role == "assistant":
            history.append(AIMessage(content=row.content))
    return history


async def save_message(db: AsyncSession, conversation_id: uuid.UUID, role: str, content: str) -> Message:
    message = Message(conversation_id=conversation_id, role=role, content=content)
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
