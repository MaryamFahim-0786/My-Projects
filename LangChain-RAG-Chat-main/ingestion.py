import asyncio
import logging
import os
import ssl

import certifi
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_tavily import TavilyCrawl
from langchain_text_splitters import RecursiveCharacterTextSplitter

from logger import *

load_dotenv()
INDEX_NAME = "langchain-doc-index"

# Configure SSL context to use certifi certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Google Gemini embeddings (free tier, no credit card required)
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# Pinecone vectorstore
vectorstore = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)

# Tavily crawler
tavily_crawl = TavilyCrawl()


async def main():
    """Main async function to orchestrate the entire process."""
    log_header("DOCUMENTATION INGESTION PIPELINE")

    log_info("🗺️  TavilyCrawl: Starting to crawl the documentation site", Colors.PURPLE)
    res = tavily_crawl.invoke(
        {
            "url": "https://python.langchain.com/",
            "max_depth": 2,
            "extract_depth": "basic",
            "max_breadth": 20,
            "limit": 50,
        }
    )
    print("TAVILY RAW RESPONSE:", res)
    if "results" not in res:
        raise SystemExit("Tavily did not return results — see raw response above.")

    all_docs = [
        Document(page_content=res["raw_content"], metadata={"source": res["url"]})
        for res in res["results"]
        if res.get("raw_content")
    ]

    # Split documents into chunks
    log_header("DOCUMENT CHUNKING PHASE")
    log_info(
        f"✂️  Text Splitter: Processing {len(all_docs)} documents with 1000 chunk size and 150 overlap",
        Colors.YELLOW,
    )
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    splitted_docs = text_splitter.split_documents(all_docs)
    log_success(
        f"Text Splitter: Created {len(splitted_docs)} chunks from {len(all_docs)} documents"
    )

    # Ingestion loop (no asyncio needed)
    log_header("VECTOR STORAGE PHASE")
    BATCH = 200  # Pinecone upsert batch size (50–200 is safe)
    for i in range(0, len(splitted_docs), BATCH):
        batch = splitted_docs[i : i + BATCH]
        vectorstore.add_documents(batch)
        log_success(
            f"VectorStore Indexing: Upserted {min(i+BATCH, len(splitted_docs))}/{len(splitted_docs)} chunks"
        )

    log_header("PIPELINE COMPLETE")
    log_success("🎉 Documentation ingestion pipeline finished successfully!")
    log_info("📊 Summary:", Colors.BOLD)
    log_info(f"   • Documents extracted: {len(all_docs)}")
    log_info(f"   • Chunks created: {len(splitted_docs)}")


if __name__ == "__main__":
    asyncio.run(main())