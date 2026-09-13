import os
import tempfile

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.database import get_db
from app.db.models import Document, User
from app.schemas import DocumentOut
from app.services.rag import ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {extension}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        document = await ingest_document(
            db=db,
            user_id=current_user.id,
            filename=file.filename,
            file_path=tmp_path,
            extension=extension,
        )
    finally:
        os.unlink(tmp_path)

    return document


@router.get("/", response_model=list[DocumentOut])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Document).where(Document.user_id == current_user.id))
    return result.scalars().all()
