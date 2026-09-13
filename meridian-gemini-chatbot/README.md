# Meridian — Advanced Gemini Chatbot

A production-grade, full-stack Gemini chatbot: RAG over your own documents, per-user
persistent memory, a tool-calling agent (live web search + calculator), and full
email/password authentication.

## Stack

| Layer      | Tech |
|------------|------|
| Frontend   | Next.js 14 (App Router), React, Tailwind CSS |
| Backend    | FastAPI, LangChain, `langchain-google-genai` |
| LLM        | Google Gemini (chat + `text-embedding-004` for embeddings) |
| Database   | PostgreSQL + `pgvector` (single DB for auth, chat history, and vector search) |
| Auth       | JWT (access + refresh tokens), bcrypt password hashing |

## Architecture

```
frontend/            Next.js app (login, signup, chat UI)
backend/
  app/
    api/             auth, chat, documents routers
    core/            settings, JWT + password hashing
    db/              SQLAlchemy models (users, conversations, messages, document_chunks)
    services/
      llm.py         Gemini chat + embeddings model factories
      rag.py         document ingestion, chunking, embedding, similarity retrieval
      memory.py      per-conversation history load/save
      tools.py       agent tools (web search, calculator — add your own here)
      agent.py       ties it together: RAG context + memory + tool-calling agent
docker-compose.yml    Postgres+pgvector, backend
```

### How a chat turn works
1. Frontend sends `{ message, conversation_id, use_rag, use_tools }` to `POST /api/chat/`.
2. Backend loads the last 20 messages of that conversation (short-term memory).
3. If `use_rag`, it embeds the query and pulls the top-4 most similar chunks from
   **that user's own** uploaded documents via `pgvector` cosine distance.
4. The Gemini agent (LangChain `create_tool_calling_agent`) receives the system
   prompt + RAG context + history + the new message, and can call `web_search` or
   `calculator` before answering.
5. Both the user message and the reply are persisted, and the conversation is
   auto-titled from the first message.

## Local setup

### 1. Backend
```bash
cd backend
cp .env.example .env        # fill in GOOGLE_API_KEY and JWT_SECRET_KEY
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Start Postgres with pgvector (or use `docker-compose up db`):
```bash
docker run -d --name pgvector -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=gemini_chatbot -p 5432:5432 ankane/pgvector
```

Run the API (tables + the `vector` extension are created automatically on startup):
```bash
uvicorn app.main:app --reload
```
API docs: http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```
App: http://localhost:3000

### 3. Or run everything with Docker
```bash
docker-compose up --build
```
(Run the frontend separately with `npm run dev` — it isn't containerized here
since local dev/hot-reload is smoother outside Docker; add a `frontend` service
to `docker-compose.yml` for a fully containerized deploy.)

## Deploying to production
- **Frontend** → Vercel (set `NEXT_PUBLIC_API_URL` to your backend's public URL).
- **Backend** → Railway, Render, or AWS (ECS/App Runner); set all vars from `.env.example`.
- **Database** → a managed Postgres with the `pgvector` extension available
  (Supabase and Neon both support it — enable it in their dashboard or let the
  app's startup hook run `CREATE EXTENSION IF NOT EXISTS vector`).
- Set `JWT_SECRET_KEY` to a long random value in production — never reuse the example.
- Restrict `FRONTEND_ORIGIN` (CORS) to your real deployed frontend domain.

## Extending it
- **More RAG file types**: add a loader to `LOADERS` in `app/services/rag.py`.
- **More agent tools**: add entries to `get_tools()` in `app/services/tools.py`
  (e.g. a Tavily search tool, a database lookup, an internal API call).
- **Streaming responses**: `ChatGoogleGenerativeAI` supports `.astream()` —
  swap the `/chat/` endpoint to a `StreamingResponse` if you want token-by-token output.
- **Conversation titles/summaries**: currently just the first 60 chars of the
  first message; swap in a one-line Gemini summarization call if you want smarter titles.
