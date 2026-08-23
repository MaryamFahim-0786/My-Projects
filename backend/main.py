# ============================================================
# AI WEATHER INTELLIGENCE PLATFORM
# Backend: FastAPI
# Weather: Open-Meteo
# AI: LangChain + LangGraph + Groq (OpenAI-compatible)
# ============================================================

import os
import requests

from typing import TypedDict

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START, END


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
    version="2.0.0",
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
        "version": "2.0.0",
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
# WEATHER ENDPOINT
# ============================================================

@app.get("/api/weather")
def get_weather(
    latitude: float | None = None,
    longitude: float | None = None,
    city: str | None = None,
):

    # ========================================================
    # LOCATION VARIABLES
    # ========================================================

    location_name = "Selected Location"
    country = ""
    country_code = ""

    # ========================================================
    # OPTION 1
    # LATITUDE + LONGITUDE
    # ========================================================

    if latitude is not None and longitude is not None:

        final_latitude = latitude
        final_longitude = longitude

    # ========================================================
    # OPTION 2
    # CITY NAME
    # ========================================================

    elif city:

        geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

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

        location_name = location.get(
            "name",
            city,
        )

        country = location.get(
            "country",
            "",
        )

        country_code = location.get(
            "country_code",
            "",
        )

    # ========================================================
    # INVALID REQUEST
    # ========================================================

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                "Please provide either latitude and longitude "
                "or city."
            ),
        )

    # ========================================================
    # OPEN-METEO
    # ========================================================

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

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

    # ========================================================
    # REQUEST WEATHER
    # ========================================================

    try:

        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )

        response.raise_for_status()

        weather_data = response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=500,
            detail=f"Weather API error: {error}",
        )

    # ========================================================
    # RETURN
    # ========================================================

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
        description="Location latitude",
    )

    longitude: float = Field(
        ...,
        description="Location longitude",
    )

    location_name: str = Field(
        default="Selected Location",
        description="Current location name",
    )


# ============================================================
# LANGGRAPH STATE
# ============================================================

class WeatherAgentState(TypedDict):

    question: str

    weather: dict

    location_name: str

    answer: str


# ============================================================
# GET WEATHER FOR AI
# ============================================================

def get_weather_for_ai(
    latitude: float,
    longitude: float,
):

    weather_url = (
        "https://api.open-meteo.com/v1/forecast"
    )

    weather_params = {

        "latitude": latitude,

        "longitude": longitude,

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

        response = requests.get(
            weather_url,
            params=weather_params,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        raise HTTPException(
            status_code=500,
            detail=f"Weather API error: {error}",
        )


# ============================================================
# LANGGRAPH NODE
# WEATHER
# ============================================================

def weather_node(
    state: WeatherAgentState,
):

    # Weather has already been fetched before
    # entering the graph.

    return state


# ============================================================
# LANGGRAPH NODE
# AI
# ============================================================

def ai_node(
    state: WeatherAgentState,
):

    if not GROQ_API_KEY:

        raise Exception(
            "GROQ_API_KEY is not configured."
        )

    # ========================================================
    # CREATE LLM (Groq, via OpenAI-compatible endpoint)
    # ========================================================

    llm = ChatOpenAI(

        model=GROQ_MODEL,

        temperature=0.2,

        api_key=GROQ_API_KEY,

        base_url=GROQ_BASE_URL,
    )

    # ========================================================
    # WEATHER DATA
    # ========================================================

    weather = state["weather"]

    current = weather.get(
        "current",
        {},
    )

    daily = weather.get(
        "daily",
        {},
    )

    location_name = state.get(
        "location_name",
        "Selected Location",
    )

    question = state["question"]

    # ========================================================
    # AI PROMPT
    # ========================================================

    prompt = f"""
You are the AI Weather Assistant inside an AI Weather
Intelligence Platform.

Location:
{location_name}

The user asked:

{question}

You MUST answer using the provided live weather data.

Current weather:
{current}

7-day forecast:
{daily}

Rules:

1. Do not invent weather information.
2. Use only the supplied weather data.
3. Answer directly.
4. Keep the answer concise but useful.
5. Explain weather in simple language.
6. If the question asks about rain, use precipitation
   probability and weather code where appropriate.
7. If the question asks about outdoor activities,
   give a practical recommendation based on the data.
8. If the question asks about clothing, base it on
   temperature, apparent temperature and weather conditions.
9. Mention uncertainty if the available data cannot
   completely answer the question.

Return ONLY the answer to the user.
"""

    # ========================================================
    # CALL GROQ
    # ========================================================

    response = llm.invoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    # ========================================================
    # SAVE ANSWER
    # ========================================================

    state["answer"] = response.content

    return state


# ============================================================
# BUILD LANGGRAPH
# ============================================================

def build_weather_graph():

    graph = StateGraph(
        WeatherAgentState
    )

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph.add_node(
        "weather",
        weather_node,
    )

    graph.add_node(
        "ai",
        ai_node,
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph.add_edge(
        START,
        "weather",
    )

    graph.add_edge(
        "weather",
        "ai",
    )

    graph.add_edge(
        "ai",
        END,
    )

    # --------------------------------------------------------
    # COMPILE
    # --------------------------------------------------------

    return graph.compile()


# ============================================================
# CREATE GRAPH
# ============================================================

weather_graph = build_weather_graph()


# ============================================================
# AI WEATHER ENDPOINT
# ============================================================

@app.post("/api/ai/weather")
def ask_weather_endpoint(
    request: AIWeatherRequest,
):

    # ========================================================
    # CHECK API KEY
    # ========================================================

    if not GROQ_API_KEY:

        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is not configured.",
        )

    # ========================================================
    # GET LIVE WEATHER
    # ========================================================

    try:

        weather_data = get_weather_for_ai(
            request.latitude,
            request.longitude,
        )

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to get weather data: {error}",
        )

    # ========================================================
    # INITIAL GRAPH STATE
    # ========================================================

    initial_state: WeatherAgentState = {

        "question": request.question,

        "weather": weather_data,

        "location_name": request.location_name,

        "answer": "",
    }

    # ========================================================
    # RUN LANGGRAPH
    # ========================================================

    try:

        result = weather_graph.invoke(
            initial_state
        )

    except Exception as error:

        print(
            "LANGGRAPH ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=f"AI processing error: {error}",
        )

    # ========================================================
    # RETURN AI RESPONSE
    # ========================================================

    return {

        "status": "success",

        "question": request.question,

        "location": request.location_name,

        "answer": result.get(
            "answer",
            "Unable to generate an AI response.",
        ),
    }


# ============================================================
# SIMPLE AI ENDPOINT
# ============================================================
#
# This endpoint is kept for compatibility.
#
# It accepts:
#
# {
#     "question": "...",
#     "weather_context": "..."
# }
#
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

        response = llm.invoke(
            [
                HumanMessage(
                    content=prompt
                )
            ]
        )

        return {

            "answer": response.content,

            "status": "success",
        }

    except Exception as error:

        print(
            "SIMPLE AI ERROR:",
            repr(error),
        )

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