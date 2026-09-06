# Crypto AI Assistant

Live crypto dashboard + AI market intelligence chatbot, teen parts mein:

```
crypto-ai-assistant/
├── backend/    → Flask API + LangChain agent (live prices from CoinGecko)
├── frontend/   → Next.js dashboard (price cards, live graph, AI chat panel)
└── desktop/    → Electron wrapper (frontend ko desktop app bana deta hai)
```

## 1. Backend chalayein (Flask + LangChain)

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# .env kholein aur apni API key daalein:
#   GOOGLE_API_KEY=...      (agar LLM_PROVIDER=gemini, default) — https://aistudio.google.com/apikey se free key banayein
#   ANTHROPIC_API_KEY=...   (agar LLM_PROVIDER=anthropic)
#   OPENAI_API_KEY=...      (agar LLM_PROVIDER=openai)
#   CRYPTOCOMPARE_API_KEY=... (optional — news works via free RSS without it)
#
# GEMINI_MODEL sirf valid model name hona chahiye: gemini-3.5-flash (default,
# recommended), gemini-2.5-flash, ya gemini-3-flash-preview. Invalid model
# naam se AI chat kaam nahi karega chahe API key sahi ho.

python app.py
```
Backend `http://localhost:5000` par chalega. Coin prices/graph ke liye CoinGecko ka
**free public API** use hota hai — is ke liye koi key nahi chahiye. Sirf AI chat ke
liye Anthropic ya OpenAI ki key chahiye.

## 2. Frontend chalayein (Next.js)

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```
Browser mein `http://localhost:3000` kholein — dashboard live prices, graph, aur
chat bot ke sath ready hoga (backend pehle se chalta hona chahiye).

## 3. Desktop app (Electron)

Desktop app simply frontend ko ek native window mein khol deta hai — pehle
backend aur frontend dono chal rahe hone chahiye.

```bash
cd desktop
npm install
npm start
```
Isse ek desktop window khulegi jo `http://localhost:3000` load karegi (jaisa
`main.js` mein `APP_URL` set hai). Distributable `.exe` / `.dmg` / `.AppImage`
banane ke liye:

```bash
npm run dist
```
(Production ke liye behtar hai `frontend` ko pehle deploy kar dein — jaise
Vercel par — aur `desktop/main.js` mein `APP_URL` ko us live URL par point
kar dein, taake end-users ko local servers chalane ki zaroorat na ho.)

## Features jo ready hain

- **Live price cards** — 6+ coins, har 30 second mein auto-refresh
- **Historical graph** — 7D / 30D / 90D toggle, coin dropdown se koi bhi coin select karein
- **AI chat bot** (LangChain agent) jo teen live tools use karta hai:
  - `get_live_price` — kisi bhi coin ka abhi ka price
  - `compare_coins` — multiple coins compare karna
  - `get_price_trend` — N din ka trend summary
- Roman Urdu / Hindi / English — jis language mein user poochta hai, bot usi mein reply karta hai

## Aage badhane ke ideas

- News section (screenshot mein "Crypto Market News") — ek `/api/news` endpoint
  add karke kisi crypto news API (e.g. CryptoPanic) se jodein
- Zyada coins — `backend/app.py` mein `DEFAULT_COINS` list badhayein
- Auth / saved watchlists — user accounts add karein


## Updated AI Assistant

- Voice input/output has been removed. The assistant is text-first.
- The AI command center now sits below the market dashboard.
- It includes an animated, continuously evolving market-intelligence signal line.
- CoinGecko requests use caching, retry/backoff, and an optional `COINGECKO_API_KEY`.
- CryptoCompare is used as a best-effort fallback when CoinGecko is rate-limited.
- Search supports a larger built-in coin catalog and remembers symbols discovered through search.
