"""
Crypto AI Assistant — Backend
Flask API + LangChain agent, resilient crypto market data.

CoinGecko is used when available. CryptoCompare is a best-effort fallback so
the dashboard keeps working when CoinGecko returns HTTP 429 (rate limited).
"""

import os
import time
from functools import lru_cache

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

COINGECKO_BASE = "https://api.coingecko.com/api/v3"
CRYPTOCOMPARE_BASE = "https://min-api.cryptocompare.com/data"

# In-memory cache. Longer TTL means fewer upstream requests and fewer 429s.
_cache = {}
CACHE_TTL_SECONDS = 120
STALE_TTL_SECONDS = 3600
coin_symbol_cache = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "binancecoin": "BNB",
    "solana": "SOL",
    "dogecoin": "DOGE",
    "ripple": "XRP",
    "cardano": "ADA",
    "polkadot": "DOT",
    "avalanche-2": "AVAX",
    "chainlink": "LINK",
    "uniswap": "UNI",
    "litecoin": "LTC",
    "stellar": "XLM",
    "tron": "TRX",
    "shiba-inu": "SHIB",
    "polygon": "POL",
}

coin_name_cache = {
    "bitcoin": "Bitcoin",
    "ethereum": "Ethereum",
    "binancecoin": "BNB",
    "solana": "Solana",
    "dogecoin": "Dogecoin",
    "ripple": "XRP",
    "cardano": "Cardano",
    "polkadot": "Polkadot",
    "avalanche-2": "Avalanche",
    "chainlink": "Chainlink",
    "uniswap": "Uniswap",
    "litecoin": "Litecoin",
    "stellar": "Stellar",
    "tron": "TRON",
    "shiba-inu": "Shiba Inu",
    "polygon": "Polygon",
}

COINGECKO_KEY = os.getenv("COINGECKO_API_KEY", "").strip()
CRYPTOCOMPARE_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "").strip()


def _cache_key(url, params=None):
    return (url, tuple(sorted((params or {}).items())))


def cached_get(url, params=None, ttl=CACHE_TTL_SECONDS, allow_stale=True):
    """GET with caching, exponential retry for 429, and stale-cache fallback."""
    key = _cache_key(url, params)
    now = time.time()
    entry = _cache.get(key)

    if entry and now - entry["time"] < ttl:
        return entry["data"]

    headers = {
        "User-Agent": "CryptoAI-Assistant/2.0",
        "Accept": "application/json",
    }
    if "coingecko.com" in url and COINGECKO_KEY:
        # Supports CoinGecko Demo/Pro keys without hard-coding a secret.
        headers["x-cg-demo-api-key"] = COINGECKO_KEY
    if "cryptocompare.com" in url and CRYPTOCOMPARE_KEY:
        # CryptoCompare now rate-limits/blocks most unauthenticated requests,
        # especially the news endpoint. Free key: min-api.cryptocompare.com/pricing
        headers["authorization"] = f"Apikey {CRYPTOCOMPARE_KEY}"

    last_error = None
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=12)
            if resp.status_code == 429:
                last_error = requests.HTTPError("CoinGecko rate limit (429)")
                time.sleep(1.5 * (attempt + 1))
                continue
            resp.raise_for_status()
            data = resp.json()
            _cache[key] = {"time": now, "data": data}
            return data
        except requests.RequestException as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(0.7 * (attempt + 1))

    if allow_stale and entry:
        return entry["data"]
    raise last_error or requests.RequestException("Request failed")


def _coin_ids(ids):
    return [x.strip() for x in ids.split(",") if x.strip()]


def _cryptocompare_prices(ids):
    symbols = []
    id_for_symbol = {}
    for coin_id in _coin_ids(ids):
        symbol = coin_symbol_cache.get(coin_id)
        if symbol:
            symbols.append(symbol)
            id_for_symbol[symbol.upper()] = coin_id

    if not symbols:
        return []

    data = cached_get(
        f"{CRYPTOCOMPARE_BASE}/pricemultifull",
        params={"fsyms": ",".join(dict.fromkeys(symbols)), "tsyms": "USD"},
        ttl=120,
    )
    raw = data.get("RAW", {})
    result = []
    for symbol, payload in raw.items():
        usd = payload.get("USD", {})
        coin_id = id_for_symbol.get(symbol.upper())
        if not coin_id:
            continue
        result.append({
            "id": coin_id,
            "symbol": symbol.upper(),
            "name": coin_name_cache.get(coin_id, symbol.upper()),
            "price": usd.get("PRICE"),
            "change_24h": round(usd.get("CHANGEPCT24HOUR") or 0, 2),
            "market_cap": usd.get("MKTCAP"),
            "volume_24h": usd.get("VOLUME24HOUR"),
            "image": None,
        })
    return result


def market_prices(ids):
    """CoinGecko first, CryptoCompare fallback."""
    try:
        data = cached_get(
            f"{COINGECKO_BASE}/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": ids,
                "order": "market_cap_desc",
                "price_change_percentage": "24h",
            },
            ttl=120,
        )
        return [
            {
                "id": c["id"],
                "symbol": c["symbol"].upper(),
                "name": c["name"],
                "price": c["current_price"],
                "change_24h": round(c.get("price_change_percentage_24h") or 0, 2),
                "market_cap": c["market_cap"],
                "volume_24h": c["total_volume"],
                "image": c.get("image"),
            }
            for c in data
        ]
    except requests.RequestException:
        return _cryptocompare_prices(ids)


# ---------------------------------------------------------------------------
# Market data endpoints
# ---------------------------------------------------------------------------

DEFAULT_COINS = ["bitcoin", "ethereum", "binancecoin", "solana", "dogecoin", "ripple"]


@app.get("/api/coins")
def list_coins():
    coins = [
        {"id": "bitcoin", "symbol": "BTC", "name": "Bitcoin"},
        {"id": "ethereum", "symbol": "ETH", "name": "Ethereum"},
        {"id": "binancecoin", "symbol": "BNB", "name": "BNB"},
        {"id": "solana", "symbol": "SOL", "name": "Solana"},
        {"id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin"},
        {"id": "ripple", "symbol": "XRP", "name": "XRP"},
        {"id": "cardano", "symbol": "ADA", "name": "Cardano"},
        {"id": "polkadot", "symbol": "DOT", "name": "Polkadot"},
        {"id": "avalanche-2", "symbol": "AVAX", "name": "Avalanche"},
        {"id": "chainlink", "symbol": "LINK", "name": "Chainlink"},
        {"id": "uniswap", "symbol": "UNI", "name": "Uniswap"},
        {"id": "litecoin", "symbol": "LTC", "name": "Litecoin"},
        {"id": "stellar", "symbol": "XLM", "name": "Stellar"},
        {"id": "tron", "symbol": "TRX", "name": "TRON"},
        {"id": "shiba-inu", "symbol": "SHIB", "name": "Shiba Inu"},
        {"id": "polygon", "symbol": "POL", "name": "Polygon"},
    ]
    return jsonify(coins)


@app.get("/api/prices")
def get_prices():
    ids = request.args.get("ids", ",".join(DEFAULT_COINS))
    try:
        result = market_prices(ids)
        return jsonify(result)
    except requests.RequestException as e:
        return jsonify({
            "error": "Live market providers are temporarily rate-limited. Please try again in a moment.",
            "details": str(e),
        }), 503


@app.get("/api/search")
def search_coins():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    # CoinGecko search gives the richest results.
    try:
        data = cached_get(
            f"{COINGECKO_BASE}/search",
            params={"query": q},
            ttl=300,
        )
        coins = data.get("coins", [])[:10]
        result = []
        for c in coins:
            coin_symbol_cache[c["id"]] = c["symbol"].upper()
            coin_name_cache[c["id"]] = c["name"]
            result.append({
                "id": c["id"],
                "symbol": c["symbol"].upper(),
                "name": c["name"],
                "thumb": c.get("thumb"),
            })
        if result:
            return jsonify(result)
    except requests.RequestException:
        pass

    # Fallback search over our expanded local catalog.
    ql = q.lower()
    result = []
    for coin_id, symbol in coin_symbol_cache.items():
        name = coin_name_cache.get(coin_id, symbol)
        if ql in coin_id.lower() or ql in symbol.lower() or ql in name.lower():
            result.append({"id": coin_id, "symbol": symbol, "name": name, "thumb": None})
    return jsonify(result[:10])


import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

RSS_NEWS_FEEDS = [
    ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    ("Cointelegraph", "https://cointelegraph.com/rss"),
]


def _fetch_rss_news(limit=8):
    """Key-free fallback: pull headlines straight from public RSS feeds."""
    articles = []
    errors = []

    for source_name, feed_url in RSS_NEWS_FEEDS:
        try:
            resp = requests.get(
                feed_url,
                headers={"User-Agent": "CryptoAI-Assistant/2.0"},
                timeout=10,
            )
            resp.raise_for_status()
            root = ET.fromstring(resp.content)

            for item in root.findall(".//item")[:limit]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub_date_raw = item.findtext("pubDate")
                if not title or not link:
                    continue
                try:
                    published_on = int(parsedate_to_datetime(pub_date_raw).timestamp())
                except Exception:
                    published_on = int(time.time())

                articles.append({
                    "title": title,
                    "source": source_name,
                    "url": link,
                    "published_on": published_on,
                    "body": "",
                })
        except Exception as e:
            errors.append(f"{source_name}: {e}")

    articles.sort(key=lambda a: a["published_on"], reverse=True)
    return articles[:limit], errors


@app.get("/api/news")
def get_news():
    # Prefer CryptoCompare only if a key is configured (it now hard-blocks
    # unauthenticated requests). Otherwise go straight to free RSS feeds.
    if CRYPTOCOMPARE_KEY:
        try:
            data = cached_get(
                f"{CRYPTOCOMPARE_BASE}/v2/news/",
                params={"lang": "EN"},
                ttl=300,
            )
            if isinstance(data, dict) and data.get("Data"):
                articles = data.get("Data", [])[:8]
                result = [
                    {
                        "title": a["title"],
                        "source": a.get("source_info", {}).get("name", a.get("source", "")),
                        "url": a["url"],
                        "published_on": a["published_on"],
                        "body": (a.get("body") or "")[:180],
                    }
                    for a in articles
                    if "title" in a and "url" in a and "published_on" in a
                ]
                if result:
                    return jsonify(result)
        except Exception as e:
            print(f"NEWS: CryptoCompare failed, falling back to RSS: {e!r}")

    articles, errors = _fetch_rss_news()
    if articles:
        return jsonify(articles)

    return jsonify({
        "error": "Could not fetch news from any source right now. "
                 f"({'; '.join(errors) if errors else 'no details'})"
    }), 502


def _history_fallback(coin_id, days):
    symbol = coin_symbol_cache.get(coin_id)
    if not symbol:
        return []

    try:
        days_i = max(1, min(int(days), 90))
    except ValueError:
        days_i = 30

    # CryptoCompare histoday returns a compact daily series and is used only
    # when CoinGecko is unavailable.
    data = cached_get(
        f"{CRYPTOCOMPARE_BASE}/v2/histoday",
        params={"fsym": symbol, "tsym": "USD", "limit": days_i},
        ttl=300,
    )
    return [
        {"timestamp": int(p["time"]) * 1000, "price": p["close"]}
        for p in data.get("Data", {}).get("Data", [])
        if p.get("close") is not None
    ]


@app.get("/api/history/<coin_id>")
def get_history(coin_id):
    days = request.args.get("days", "30")
    symbol = request.args.get("symbol", "").strip().upper()
    if symbol:
        coin_symbol_cache[coin_id] = symbol

    try:
        data = cached_get(
            f"{COINGECKO_BASE}/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days},
            ttl=300,
        )
        points = [{"timestamp": ts, "price": price} for ts, price in data.get("prices", [])]
        return jsonify({"coin_id": coin_id, "days": days, "points": points})
    except requests.RequestException as coingecko_err:
        print(f"HISTORY: CoinGecko failed for {coin_id} ({days}d): {coingecko_err!r}")
        try:
            points = _history_fallback(coin_id, days)
            return jsonify({"coin_id": coin_id, "days": days, "points": points, "source": "fallback"})
        except requests.RequestException as fallback_err:
            print(f"HISTORY: CryptoCompare fallback also failed for {coin_id} ({days}d): {fallback_err!r}")
            hint = (
                "" if CRYPTOCOMPARE_KEY else
                " Add a free CRYPTOCOMPARE_API_KEY in backend/.env, or a "
                "COINGECKO_API_KEY (https://www.coingecko.com/en/api/pricing) "
                "to avoid CoinGecko's free-tier rate limits."
            )
            return jsonify({
                "coin_id": coin_id,
                "days": days,
                "points": [],
                "error": f"CoinGecko: {coingecko_err}. CryptoCompare fallback: {fallback_err}.{hint}",
            }), 503


# ---------------------------------------------------------------------------
# AI Chat — Gemini without function calling
# ---------------------------------------------------------------------------

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()


def get_llm():
    if LLM_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        google_key = os.getenv("GOOGLE_API_KEY", "").strip()
        if not google_key:
            raise ValueError("GOOGLE_API_KEY is missing in backend/.env")

        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
            google_api_key=google_key,
        )

    if LLM_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.3,
        )

    if LLM_PROVIDER == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5"),
            temperature=0.3,
        )

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")


SYSTEM_PROMPT = """
You are Crypto AI Bot, a polished crypto market intelligence assistant.

- Answer in the same language/style as the user.
- Use the LIVE MARKET CONTEXT supplied by the backend.
- Never invent current crypto prices or statistics.
- If live data is unavailable, say so clearly.
- Be concise, useful, and easy to understand.
- Use USD formatting.
"""


def _detect_coin_ids(message):
    text = message.lower()

    aliases = {
        "bitcoin": "bitcoin", "btc": "bitcoin",
        "ethereum": "ethereum", "eth": "ethereum",
        "bnb": "binancecoin", "binance": "binancecoin",
        "solana": "solana", "sol": "solana",
        "dogecoin": "dogecoin", "doge": "dogecoin",
        "xrp": "ripple", "ripple": "ripple",
        "cardano": "cardano", "ada": "cardano",
        "polkadot": "polkadot", "dot": "polkadot",
        "avalanche": "avalanche-2", "avax": "avalanche-2",
        "chainlink": "chainlink", "link": "chainlink",
        "uniswap": "uniswap", "uni": "uniswap",
        "litecoin": "litecoin", "ltc": "litecoin",
        "stellar": "stellar", "xlm": "stellar",
        "tron": "tron", "trx": "tron",
        "shiba": "shiba-inu", "shib": "shiba-inu",
        "polygon": "polygon", "pol": "polygon",
    }

    found = []
    for alias, coin_id in aliases.items():
        if alias in text and coin_id not in found:
            found.append(coin_id)
    return found


def get_market_context(message):
    coin_ids = _detect_coin_ids(message)

    if not coin_ids:
        coin_ids = [
            "bitcoin", "ethereum", "binancecoin",
            "solana", "dogecoin", "ripple"
        ]

    try:
        data = market_prices(",".join(coin_ids))
    except Exception as e:
        return f"Live market data unavailable: {e}"

    if not data:
        return "No live market data was returned."

    lines = []
    for coin in data:
        price = coin.get("price")
        change = coin.get("change_24h")
        market_cap = coin.get("market_cap")

        if isinstance(price, (int, float)):
            price_text = f"${price:,.6f}" if price < 1 else f"${price:,.2f}"
        else:
            price_text = "N/A"

        change_text = f"{change:+.2f}%" if isinstance(change, (int, float)) else "N/A"
        cap_text = f"${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else "N/A"

        lines.append(
            f"- {coin.get('name', 'Unknown')} ({coin.get('symbol', '')}): "
            f"Price {price_text}, 24h {change_text}, Market Cap {cap_text}"
        )

    text = message.lower()
    if any(word in text for word in [
        "trend", "7-day", "7 day", "30-day", "30 day",
        "history", "performance"
    ]):
        trend_coin = coin_ids[0]
        days = "30" if "30" in text else "7"
        trend = get_price_trend_data(trend_coin, days)
        if trend:
            lines.extend(["", "Trend analysis:", trend])

    return "\n".join(lines)


def get_price_trend_data(coin_id, days="7"):
    """Fetch trend data server-side; Gemini never calls this as a tool."""
    try:
        data = cached_get(
            f"{COINGECKO_BASE}/coins/{coin_id}/market_chart",
            params={"vs_currency": "usd", "days": days},
            ttl=300,
        )
        prices = [p for _, p in data.get("prices", [])]
        if not prices:
            raise requests.RequestException("No CoinGecko history")
    except Exception:
        try:
            prices = [p["price"] for p in _history_fallback(coin_id, days)]
        except Exception as e:
            return f"{coin_id} trend unavailable: {e}"

    start_price = prices[0]
    end_price = prices[-1]
    pct = ((end_price - start_price) / start_price * 100) if start_price else 0

    return (
        f"{coin_id} over the last {days} days: "
        f"start ${start_price:,.2f}, current ${end_price:,.2f}, "
        f"change {pct:+.2f}%, high ${max(prices):,.2f}, "
        f"low ${min(prices):,.2f}."
    )


@app.post("/api/chat")
def chat():
    body = request.get_json(force=True) or {}
    message = body.get("message", "").strip()
    history = body.get("history", [])

    if not message:
        return jsonify({"error": "message is required"}), 400

    try:
        market_context = get_market_context(message)

        messages = [SystemMessage(content=SYSTEM_PROMPT)]

        for item in history[-8:]:
            content = item.get("content", "")
            if not content:
                continue

            if item.get("role") == "user":
                messages.append(HumanMessage(content=content))
            elif item.get("role") == "assistant":
                messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=f"""
User question:
{message}

LIVE MARKET CONTEXT:
{market_context}

Answer using the live context above. Do not invent current market numbers.
Do not say you personally performed an API call.
"""))

        # IMPORTANT: direct Gemini invocation, NO tools/agent/function calling.
        llm = get_llm()
        response = llm.invoke(messages)
        reply = response.content

        if isinstance(reply, list):
            reply = "".join(
                part if isinstance(part, str)
                else str(part.get("text", "")) if isinstance(part, dict)
                else str(part)
                for part in reply
            )

        return jsonify({
            "reply": reply or "I couldn't generate a response right now."
        })

    except Exception as e:
        print("AI ERROR:", repr(e))
        return jsonify({
            "reply": f"AI backend error. Details: {e}"
        })


@app.get("/")
def root():
    return jsonify({
        "status": "ok",
        "service": "Crypto AI Assistant API",
        "message": "Backend is running.",
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Debug can be enabled with FLASK_DEBUG=1, but the default is off so
    # Windows does not spawn duplicate watchdog/reloader processes.
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
