from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Conversation, Message, User
from app.schemas import ChatRequest, ConversationOut, MessageOut
from app.services.agent import run_agent
from app.services.memory import get_or_create_conversation, load_history, save_message
from app.services.rag import retrieve_context

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conversation = await get_or_create_conversation(db, current_user.id, payload.conversation_id)

    history = await load_history(db, conversation.id)

    rag_context: list[str] = []
    if payload.use_rag:
        rag_context = await retrieve_context(db, current_user.id, payload.message)

    reply = await run_agent(
        user_message=payload.message,
        history=history,
        rag_context=rag_context,
        use_tools=payload.use_tools,
    )

    await save_message(db, conversation.id, "user", payload.message)
    await save_message(db, conversation.id, "assistant", reply)

    # Auto-title new conversations from the first message
    if conversation.title == "New chat":
        conversation.title = payload.message[:60]
        await db.commit()

    return {
        "conversation_id": conversation.id,
        "reply": reply,
        "used_context": bool(rag_context),
    }


@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.user_id == current_user.id)
        .order_by(Conversation.created_at.desc())
    )
    return result.scalars().all()


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
async def get_messages(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Message)
        .join(Conversation)
        .where(Conversation.id == conversation_id, Conversation.user_id == current_user.id)
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()
