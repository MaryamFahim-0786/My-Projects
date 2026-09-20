import os
import asyncio
import logging
from typing import List, Optional

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_community.retrievers import BM25Retriever
from langchain.docstore.document import Document
from langchain_core.retrievers import BaseRetriever

logger = logging.getLogger(__name__)

# --- Configuration ---
DATA_DIR_PATH = "app/data/"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# --- Singleton ---
_retriever: Optional[BaseRetriever] = None


def _load_documents_from_disk() -> List[Document]:
    """
    Loads TXT and PDF files from the portfolio knowledge base
    and splits them into searchable chunks.
    """

    if not os.path.exists(DATA_DIR_PATH):
        os.makedirs(DATA_DIR_PATH)
        return []

    logger.info(f"Loading documents from {DATA_DIR_PATH}...")

    text_loader = DirectoryLoader(
        DATA_DIR_PATH,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"autodetect_encoding": True},
    )

    pdf_loader = DirectoryLoader(
        DATA_DIR_PATH,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,
    )

    raw_docs = text_loader.load() + pdf_loader.load()

    if not raw_docs:
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    split_docs = text_splitter.split_documents(raw_docs)

    logger.info(f"Processed {len(split_docs)} document chunks.")

    return split_docs


async def ingest_data():
    """
    Initializes the portfolio RAG retriever.

    Uses BM25 keyword search locally.
    No Gemini embedding API is required.

    Gemini is still used separately for generating chatbot answers.
    """

    global _retriever

    if _retriever is not None:
        return

    logger.info("Initializing BM25 Search retriever...")

    # Load portfolio documents
    documents = await asyncio.to_thread(_load_documents_from_disk)

    if not documents:
        logger.warning("No documents found. Using placeholder content.")

        documents = [
            Document(
                page_content="Portfolio is currently empty.",
                metadata={"source": "system"},
            )
        ]

    # Local keyword-based retrieval
    bm25_retriever = BM25Retriever.from_documents(documents)

    # Return top 5 relevant chunks
    bm25_retriever.k = 5

    _retriever = bm25_retriever

    logger.info(
        "BM25 Search retriever is ready. "
        "Gemini embeddings are not used."
    )


def get_retriever() -> BaseRetriever:
    """
    Returns the initialized retriever.
    """

    global _retriever

    if _retriever is None:
        raise RuntimeError(
            "Retriever not initialized. Ensure 'ingest_data()' runs on startup."
        )

    return _retriever


def is_retriever_ready() -> bool:
    """
    Checks whether the retriever is initialized.
    """

    return _retriever is not None