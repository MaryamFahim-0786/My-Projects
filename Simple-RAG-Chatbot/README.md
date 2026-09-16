# Simple RAG Chatbot (Gemini + FastAPI + Postgres/pgvector)

A deliberately lean RAG project — matches the shape of a "Project 9: Simple RAG
Chatbot" assignment, but built with a real production-style RAG pipeline
instead of a toy one.

## Stack
- **Backend**: FastAPI, Python, Pydantic models (no LangChain — direct
  `google-generativeai` SDK calls, to keep the dependency footprint small
  and the code easy to read end-to-end)
- **Database**: PostgreSQL + `pgvector` (works great on Supabase)
- **LLM**: Gemini for both chat and embeddings (`gemini-embedding-001`)
- **Frontend**: a single static HTML/JS page served by FastAPI itself —
  no build step, no Node required

## What makes it "advanced" for a simple project
- Multi-file upload (PDF, DOCX, TXT, MD, CSV), each chunked and embedded
- Real vector similarity search via `pgvector`, not a keyword match
- Answers cite which retrieved chunks were used
- Session-based chat history (persisted in Postgres, survives a page refresh)
- Clean separation: `services/gemini.py` (LLM calls), `services/rag.py`
  (ingestion + retrieval), `services/history.py` (chat memory)

## Setup

```bash
cp .env.example .env      # add your GOOGLE_API_KEY
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Start Postgres with pgvector (skip this if using Supabase — just point
`DATABASE_URL` at your Supabase connection string instead):
```bash
docker run -d --name simple-rag-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=simple_rag -p 5433:5432 ankane/pgvector
```
(Note: port `5433` here so it doesn't collide with the Meridian project's
Postgres on `5432` if both are running at once. Update `DATABASE_URL`
in `.env` to match whichever port you use.)

Run it:
```bash
uvicorn app.main:app --reload --port 8001
```
Open http://localhost:8001 — upload a document, then ask questions about it.

## Notes
- No login/auth — this is intentionally single-session, matching the
  "simple" brief. Chat history is scoped by a random session ID stored
  in the browser's localStorage, not a user account.
- If you outgrow this, `gemini-chatbot/` (Meridian) next to this folder
  is the advanced version with full auth, agent tools, and per-user memory.
