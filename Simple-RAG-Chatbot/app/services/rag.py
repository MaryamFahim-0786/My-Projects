import uuid

import docx2txt
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Chunk, Document
from app.services.gemini import embed_batch, embed_text


def _extract_text(file_path: str, extension: str) -> str:
    if extension == ".pdf":
        reader = PdfReader(file_path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if extension == ".docx":
        return docx2txt.process(file_path)
    # .txt / .md / .csv
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Simple sliding-window chunker — no extra dependency needed for a 'simple' RAG project."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


async def ingest_document(db: AsyncSession, filename: str, file_path: str, extension: str) -> Document:
    text = _extract_text(file_path, extension)
    pieces = _chunk_text(text)

    if not pieces:
        raise ValueError("No extractable text found in this file.")

    vectors = embed_batch(pieces, task_type="retrieval_document")

    document = Document(filename=filename)
    db.add(document)
    await db.flush()

    for piece, vector in zip(pieces, vectors):
        db.add(Chunk(document_id=document.id, content=piece, embedding=vector))

    await db.commit()
    await db.refresh(document)
    return document


async def retrieve_context(db: AsyncSession, query: str, top_k: int = 4) -> list[str]:
    query_vector = embed_text(query, task_type="retrieval_query")

    stmt = select(Chunk.content).order_by(Chunk.embedding.cosine_distance(query_vector)).limit(top_k)
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]


async def list_documents(db: AsyncSession) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc()))
    return list(result.scalars().all())
