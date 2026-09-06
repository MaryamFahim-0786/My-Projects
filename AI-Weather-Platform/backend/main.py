# ============================================================
# AI WEATHER INTELLIGENCE PLATFORM
# Backend: FastAPI
# Weather: Open-Meteo
# AI: LangChain + LangGraph + Groq (OpenAI-compatible)
# ============================================================

import os
import requests

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from ai_agent import ask_weather_ai


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="AI Weather Platform API",
    description="Backend API for the AI Weather Intelligence Platform",
    version="2.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Weather Platform Backend is running!",
        "version": "2.1.0",
        "langchain": True,
        "langgraph": True,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "backend": "FastAPI",
        "langchain": True,
        "langgraph": True,
        "groq_configured": bool(GROQ_API_KEY),
    }


# ============================================================
# WEATHER ENDPOINT (used by the search bar / map / dashboard)
# ============================================================

@app.get("/api/weather")
def get_weather(
    latitude: float | None = None,
    longitude: float | None = None,
    city: str | None = None,
):

    location_name = "Selected Location"
    country = ""
    country_code = ""

    if latitude is not None and longitude is not None:

        final_latitude = latitude
        final_longitude = longitude

    elif city:

        geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

        geocoding_params = {
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        }

        try:
            response = requests.get(
                geocoding_url,
                params=geocoding_params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

        except requests.RequestException as error:
            raise HTTPException(
                status_code=500,
                detail=f"Geocoding API error: {error}",
            )

        if not data.get("results"):
            raise HTTPException(
                status_code=404,
                detail=f"City '{city}' not found.",
            )

        location = data["results"][0]

        final_latitude = location["latitude"]
        final_longitude = location["longitude"]

        location_name = location.get("name", city)
        country = location.get("country", "")
        country_code = location.get("country_code", "")

    else:
        raise HTTPException(
            status_code=400,
            detail="Please provide either latitude and longitude or city.",
        )

    weather_url = "https://api.open-meteo.com/v1/forecast"

    weather_params = {
        "latitude": final_latitude,
        "longitude": final_longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "weather_code,"
            "wind_speed_10m"
        ),
        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation_probability,"
            "weather_code"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"
        ),
        "timezone": "auto",
        "forecast_days": 7,
    }

    try:
        response = requests.get(weather_url, params=weather_params, timeout=10)
        response.raise_for_status()
        weather_data = response.json()

    except requests.RequestException as error:
        raise HTTPException(
            status_code=500,
            detail=f"Weather API error: {error}",
        )

    return {
        "location": {
            "name": location_name,
            "country": country,
            "country_code": country_code,
            "latitude": final_latitude,
            "longitude": final_longitude,
        },
        "weather": weather_data,
    }


# ============================================================
# EARTHQUAKE ENDPOINT (dashboard card)
# ------------------------------------------------------------
# Uses USGS — free, no API key, real-time, global coverage.
# ============================================================

EARTHQUAKE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


@app.get("/api/earthquakes")
def get_earthquakes(
    latitude: float,
    longitude: float,
    radius_km: float = 500,
    min_magnitude: float = 2.5,
    days: int = 30,
):

    params = {
        "format": "geojson",
        "latitude": latitude,
        "longitude": longitude,
        "maxradiuskm": radius_km,
        "minmagnitude": min_magnitude,
        "orderby": "time",
        "limit": 15,
    }

    try:
        response = requests.get(EARTHQUAKE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        raise HTTPException(
            status_code=500,
            detail=f"USGS Earthquake API error: {error}",
        )

    earthquakes = []

    for feature in data.get("features", []):

        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [None, None, None])

        earthquakes.append({
            "magnitude": properties.get("mag"),
            "place": properties.get("place"),
            "time": properties.get("time"),
            "depth_km": coordinates[2] if len(coordinates) > 2 else None,
            "latitude": coordinates[1] if len(coordinates) > 1 else None,
            "longitude": coordinates[0] if len(coordinates) > 0 else None,
            "url": properties.get("url"),
        })

    return {
        "location": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "radius_km": radius_km,
        "count": len(earthquakes),
        "earthquakes": earthquakes,
    }


# ============================================================
# AI REQUEST MODEL
# ============================================================

class AIWeatherRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="User weather question",
    )

    latitude: float = Field(
        ...,
        description="Current search-bar location latitude (fallback only)",
    )

    longitude: float = Field(
        ...,
        description="Current search-bar location longitude (fallback only)",
    )

    location_name: str = Field(
        default="Selected Location",
        description="Current search-bar location name (fallback only)",
    )


# ============================================================
# AI WEATHER ENDPOINT
# ------------------------------------------------------------
# This now delegates to ask_weather_ai() in ai_agent.py, which:
#   1. Checks if the question mentions a specific city
#      ("weather in Lahore?")
#   2. If yes -> geocodes + fetches weather for THAT city
#   3. If no  -> falls back to the search-bar location sent below
# So the AI is no longer locked to whatever the search bar says.
# ============================================================

@app.post("/api/ai/weather")
def ask_weather_endpoint(
    request: AIWeatherRequest,
):

    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured.",
        )

    try:
        result = ask_weather_ai(
            question=request.question,
            default_latitude=request.latitude,
            default_longitude=request.longitude,
            default_location_name=request.location_name,
        )

    except Exception as error:
        print("AI AGENT ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {error}",
        )

    return {
        "status": "success",
        "question": request.question,
        # this may now be DIFFERENT from request.location_name
        # if the user asked about another city
        "location": result["resolved_location"],
        "extracted_city": result["extracted_city"],
        "wants_earthquake": result.get("wants_earthquake", False),
        "earthquake_count": result.get("earthquake_count", 0),
        "answer": result["answer"],
    }


# ============================================================
# SIMPLE AI ENDPOINT (kept for compatibility)
# ============================================================

class SimpleAIWeatherRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
    )

    weather_context: str = Field(
        default="",
    )


@app.post("/api/ai")
def weather_ai(
    request: SimpleAIWeatherRequest,
):

    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured.",
        )

    try:
        llm = ChatOpenAI(
            model=GROQ_MODEL,
            temperature=0.2,
            api_key=GROQ_API_KEY,
            base_url=GROQ_BASE_URL,
        )

        prompt = f"""
You are an AI Weather Assistant.

Answer the user's question using the provided
weather context.

Weather context:
{request.weather_context}

User question:
{request.question}

Do not invent information.

Give a concise and useful answer.
"""

        response = llm.invoke([HumanMessage(content=prompt)])

        return {
            "answer": response.content,
            "status": "success",
        }

    except Exception as error:
        print("SIMPLE AI ERROR:", repr(error))
        raise HTTPException(
            status_code=500,
            detail=f"AI error: {error}",
        )


# ============================================================
# STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
def startup_event():
    print("")
    print("=" * 60)
    print("AI WEATHER INTELLIGENCE PLATFORM")
    print("=" * 60)
    print("FastAPI       : READY")
    print("Open-Meteo    : READY")
    print("LangChain     : READY")
    print("LangGraph     : READY")
    print(
        "Groq API      :",
        "CONFIGURED" if GROQ_API_KEY else "NOT CONFIGURED",
    )
    print("=" * 60)
    print("")