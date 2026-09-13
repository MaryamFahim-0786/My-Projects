# Maryam's News

A full-stack AI news assistant: a FastAPI backend that pulls live headlines and
runs Google Gemini for summaries and chat, and a React (Vite) frontend styled
as a modern editorial reading experience with an "AI Briefing" panel docked
alongside the feed.

## Architecture

```
maryams-news/
├── backend/          FastAPI service
│   └── app/
│       ├── main.py           app entrypoint + CORS
│       ├── config.py         env-driven settings
│       ├── models/           pydantic schemas
│       ├── routers/          /api/news, /api/chat, /api/summarize
│       └── services/         NewsAPI client, Gemini client
└── frontend/         React (Vite) app
    └── src/
        ├── App.jsx            page state & data flow
        ├── api/client.js      fetch wrapper for the backend
        └── components/        Masthead, CategoryNav, FeaturedStory,
                                ArticleList/Item, AIBriefing, StateBlocks
```

**Features**

- Live top headlines by category (Top, Business, Technology, Sports, Health,
  Science, Entertainment) plus full-text search, via NewsAPI.org.
- One-click AI summary on any article, expanding inline into a short summary
  and key points, powered by Gemini.
- "AI Briefing" — a persistent chat panel for asking questions about the news;
  click "Ask AI Briefing" on any story to bring it into the conversation as
  context.

## 1. Get your API keys

- **Gemini**: https://aistudio.google.com/app/apikey (free tier available)
- **NewsAPI.org**: https://newsapi.org/register (free tier available, good for
  local development)

## 2. Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and paste in GEMINI_API_KEY and NEWS_API_KEY

uvicorn app.main:app --reload --port 8000
```

The API will be live at `http://localhost:8000` (interactive docs at
`http://localhost:8000/docs`).

## 3. Frontend setup

```bash
cd frontend
npm install

cp .env.example .env
# VITE_API_BASE_URL defaults to http://localhost:8000 — only change this
# if your backend runs elsewhere

npm run dev
```

Open `http://localhost:5173`.

## 4. Notes for production

- Set `ALLOWED_ORIGINS` in `backend/.env` to your deployed frontend's URL.
- Run the backend behind a real ASGI server config (e.g. `uvicorn` with
  `--workers`, or behind Gunicorn) and put it behind HTTPS.
- Build the frontend with `npm run build` and serve the `dist/` folder from
  any static host (Vercel, Netlify, Nginx, etc.), pointing
  `VITE_API_BASE_URL` at your deployed backend.
- NewsAPI.org's free tier is meant for development, not a live production
  audience — check their pricing page before shipping to real users.

## Tech stack

- **Backend**: FastAPI, httpx, google-generativeai, Pydantic
- **Frontend**: React 18, Vite, plain CSS (custom design system, no UI kit)
- **AI**: Google Gemini (chat + summarization)
- **News data**: NewsAPI.org
