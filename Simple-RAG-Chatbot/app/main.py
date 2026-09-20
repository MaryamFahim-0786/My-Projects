import os
import tempfile
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Base, engine, get_db
from app.schemas import ChatMessageOut, ChatRequest, ChatResponse, DocumentOut
from app.services.gemini import generate_answer
from app.services.history import load_history, load_history_full, save_message
from app.services.rag import ingest_document, list_documents, retrieve_context

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Simple RAG Chatbot", lifespan=lifespan)


@app.post("/api/documents/upload", response_model=DocumentOut)
async def upload_document(file: UploadFile, db: AsyncSession = Depends(get_db)):
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        document = await ingest_document(db, filename=file.filename, file_path=tmp_path, extension=extension)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    finally:
        os.unlink(tmp_path)

    return document


@app.get("/api/documents", response_model=list[DocumentOut])
async def get_documents(db: AsyncSession = Depends(get_db)):
    return await list_documents(db)


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    history = await load_history(db, payload.session_id)
    context_chunks = await retrieve_context(db, payload.message)

    reply = generate_answer(payload.message, context_chunks, history)

    await save_message(db, payload.session_id, "user", payload.message)
    await save_message(db, payload.session_id, "assistant", reply)

    return ChatResponse(reply=reply, sources=context_chunks)


@app.get("/api/chat/{session_id}/history", response_model=list[ChatMessageOut])
async def get_chat_history(session_id: str, db: AsyncSession = Depends(get_db)):
    return await load_history_full(db, session_id)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve the single-page frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return FileResponse("static/index.html")
