import uuid

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentChunk
from app.services.llm import get_embeddings_model

SPLITTER = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

LOADERS = {
    ".pdf": PyPDFLoader,
    ".docx": Docx2txtLoader,
    ".txt": TextLoader,
    ".md": TextLoader,
    ".csv": TextLoader,
}


def _load_and_split(file_path: str, extension: str) -> list[str]:
    loader_cls = LOADERS.get(extension)
    if loader_cls is None:
        raise ValueError(f"Unsupported file type: {extension}")
    docs = loader_cls(file_path).load()
    chunks = SPLITTER.split_documents(docs)
    return [c.page_content for c in chunks]


async def ingest_document(
    db: AsyncSession,
    user_id: uuid.UUID,
    filename: str,
    file_path: str,
    extension: str,
) -> Document:
    """Loads a document, splits it into chunks, embeds each chunk with Gemini,
    and stores everything so it can be retrieved for RAG later."""
    texts = _load_and_split(file_path, extension)
    embeddings_model = get_embeddings_model()
    vectors = await embeddings_model.aembed_documents(texts)

    document = Document(user_id=user_id, filename=filename)
    db.add(document)
    await db.flush()  # get document.id

    for text, vector in zip(texts, vectors):
        db.add(
            DocumentChunk(
                document_id=document.id,
                user_id=user_id,
                content=text,
                embedding=vector,
            )
        )

    await db.commit()
    await db.refresh(document)
    return document


async def retrieve_context(db: AsyncSession, user_id: uuid.UUID, query: str, top_k: int = 4) -> list[str]:
    """Embeds the query and returns the top_k most relevant chunks for this user,
    scoped so users only ever retrieve their own documents."""
    embeddings_model = get_embeddings_model()
    query_vector = await embeddings_model.aembed_query(query)

    stmt = (
        select(DocumentChunk.content)
        .where(DocumentChunk.user_id == user_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
        .limit(top_k)
    )
    result = await db.execute(stmt)
    return [row[0] for row in result.all()]
