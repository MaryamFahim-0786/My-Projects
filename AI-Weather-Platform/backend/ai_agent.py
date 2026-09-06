# ============================================================
# AI WEATHER AGENT
# LangGraph agent that:
#   1. Reads the user's question
#   2. Detects if a SPECIFIC city is mentioned in the question
#   3. If yes  -> geocodes that city and fetches ITS weather
#      If no   -> falls back to the app's currently selected
#                 location (search bar location)
#   4. Generates a natural-language answer using the
#      correct, freshly-fetched weather data
# ============================================================

import os
import requests

from typing import TypedDict, Optional

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from langgraph.graph import StateGraph, START, END


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
EARTHQUAKE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

EARTHQUAKE_KEYWORDS = (
    "earthquake",
    "earthquakes",
    "quake",
    "quakes",
    "seismic",
    "tremor",
    "tremors",
    "richter",
    "aftershock",
    "aftershocks",
)


# ============================================================
# GROQ MODEL (via OpenAI-compatible endpoint)
# ============================================================

llm = ChatOpenAI(
    model=GROQ_MODEL,
    temperature=0.2,
    api_key=GROQ_API_KEY,
    base_url=GROQ_BASE_URL,
)


# ============================================================
# STATE
# ============================================================

class WeatherAIState(TypedDict):

    question: str

    # location currently selected in the app (search bar)
    default_latitude: float
    default_longitude: float
    default_location_name: str

    # city name found inside the question, if any
    extracted_city: Optional[str]

    # the location the agent actually ends up using
    latitude: float
    longitude: float
    location_name: str

    weather: dict

    # whether the question is about earthquakes/seismic activity
    wants_earthquake: bool
    earthquakes: list

    answer: str


# ============================================================
# NODE 1: EXTRACT CITY FROM QUESTION
# ============================================================

def extract_city_node(state: WeatherAIState):

    question = state["question"]

    prompt = f"""
You extract place names from weather-related questions.

Question:
"{question}"

If the question explicitly names a specific city, town, or place
(for example: "weather in Lahore", "is it raining in Karachi",
"should I carry an umbrella in Multan tomorrow"),
reply with ONLY that place name and nothing else.

If the question does NOT name any specific place
(for example: "what's the weather like?", "should I carry an umbrella?",
"is it hot today?"),
reply with exactly: NONE

Rules:
- Reply with the place name only, or NONE.
- No punctuation, no explanation, no extra words.
"""

    response = llm.invoke([HumanMessage(content=prompt)])
    extracted = response.content.strip().strip(".").strip()

    if extracted.upper() == "NONE" or len(extracted) == 0:
        extracted = None

    return {"extracted_city": extracted}


# ============================================================
# HELPER: GEOCODE A CITY NAME
# ============================================================

def geocode_city(city: str):

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json",
    }

    response = requests.get(GEOCODING_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    if not data.get("results"):
        return None

    result = data["results"][0]

    return {
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "name": result.get("name", city),
        "country": result.get("country", ""),
    }


# ============================================================
# NODE 2: RESOLVE FINAL LOCATION
# ============================================================

def resolve_location_node(state: WeatherAIState):

    extracted_city = state.get("extracted_city")

    if extracted_city:

        geocoded = geocode_city(extracted_city)

        # only override if geocoding actually found a real place
        if geocoded:
            return {
                "latitude": geocoded["latitude"],
                "longitude": geocoded["longitude"],
                "location_name": geocoded["name"],
            }

    # no city mentioned, or geocoding failed -> use search bar location
    return {
        "latitude": state["default_latitude"],
        "longitude": state["default_longitude"],
        "location_name": state["default_location_name"],
    }


# ============================================================
# NODE 3: FETCH WEATHER FOR RESOLVED LOCATION
# ============================================================

def fetch_weather_node(state: WeatherAIState):

    params = {
        "latitude": state["latitude"],
        "longitude": state["longitude"],
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

    response = requests.get(WEATHER_URL, params=params, timeout=10)
    response.raise_for_status()

    return {"weather": response.json()}


# ============================================================
# NODE 4: DETECT EARTHQUAKE INTENT
# ============================================================

def detect_earthquake_intent_node(state: WeatherAIState):

    question_lower = state["question"].lower()

    wants_earthquake = any(
        keyword in question_lower
        for keyword in EARTHQUAKE_KEYWORDS
    )

    return {"wants_earthquake": wants_earthquake}


# ============================================================
# NODE 5: FETCH EARTHQUAKE DATA (USGS)
# ============================================================

def fetch_earthquake_node(state: WeatherAIState):

    if not state.get("wants_earthquake"):
        return {"earthquakes": []}

    params = {
        "format": "geojson",
        "latitude": state["latitude"],
        "longitude": state["longitude"],
        "maxradiuskm": 500,
        "minmagnitude": 2.5,
        "orderby": "time",
        "limit": 10,
    }

    try:
        response = requests.get(EARTHQUAKE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    except requests.RequestException:
        # Don't fail the whole answer if USGS is unreachable —
        # just answer without earthquake data and let the LLM
        # say it couldn't retrieve it.
        return {"earthquakes": []}

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
            "url": properties.get("url"),
        })

    return {"earthquakes": earthquakes}


# ============================================================
# NODE 6: GENERATE FINAL ANSWER
# ============================================================

def generate_answer_node(state: WeatherAIState):

    question = state["question"]
    weather = state["weather"]
    location_name = state["location_name"]
    earthquakes = state.get("earthquakes", [])
    wants_earthquake = state.get("wants_earthquake", False)

    current = weather.get("current", {})
    daily = weather.get("daily", {})

    earthquake_section = "Not requested for this question."

    if wants_earthquake:
        if earthquakes:
            earthquake_section = (
                f"{len(earthquakes)} earthquake(s) of magnitude 2.5+ "
                f"within 500km of {location_name} in the last 30 days:\n"
                f"{earthquakes}"
            )
        else:
            earthquake_section = (
                "No earthquakes of magnitude 2.5+ were recorded within "
                f"500km of {location_name} in the last 30 days, "
                "according to USGS."
            )

    prompt = f"""
You are an AI Weather Assistant that can also report on
recent earthquake / seismic activity using live USGS data.

Location the data below belongs to: {location_name}

User question:
{question}

Current weather:
{current}

7-day forecast:
{daily}

Recent earthquake activity (USGS, within 500km, last 30 days):
{earthquake_section}

Rules:
1. Answer using ONLY the data provided above.
2. Do not invent weather or earthquake information.
3. Keep the answer concise, clear, and in simple language.
4. If the question is about rain, use precipitation probability
   and weather code.
5. If the question is about outdoor activities or clothing,
   give a practical recommendation based on temperature and
   apparent temperature.
6. If the question is about earthquakes or seismic safety, use
   the earthquake data above. Mention the largest recent magnitude
   and how many events were recorded, if any. If none were recorded,
   say so plainly and note this is not a guarantee of future safety.
7. Mention the location name naturally in your answer so the
   user knows which place the data covers.

Return ONLY the answer to the user.
"""

    response = llm.invoke([HumanMessage(content=prompt)])

    return {"answer": response.content}


# ============================================================
# BUILD GRAPH
# ============================================================

graph_builder = StateGraph(WeatherAIState)

graph_builder.add_node("extract_city", extract_city_node)
graph_builder.add_node("resolve_location", resolve_location_node)
graph_builder.add_node("detect_earthquake_intent", detect_earthquake_intent_node)
graph_builder.add_node("fetch_weather", fetch_weather_node)
graph_builder.add_node("fetch_earthquake", fetch_earthquake_node)
graph_builder.add_node("generate_answer", generate_answer_node)

graph_builder.add_edge(START, "extract_city")
graph_builder.add_edge("extract_city", "resolve_location")
graph_builder.add_edge("resolve_location", "detect_earthquake_intent")
graph_builder.add_edge("detect_earthquake_intent", "fetch_weather")
graph_builder.add_edge("fetch_weather", "fetch_earthquake")
graph_builder.add_edge("fetch_earthquake", "generate_answer")
graph_builder.add_edge("generate_answer", END)

weather_ai_graph = graph_builder.compile()


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def ask_weather_ai(
    question: str,
    default_latitude: float,
    default_longitude: float,
    default_location_name: str = "Selected Location",
):
    """
    Runs the full agent:
    extract city -> resolve location -> fetch weather -> answer.

    Falls back to (default_latitude, default_longitude,
    default_location_name) — i.e. the app's search bar location —
    whenever the question doesn't mention a specific place.
    """

    result = weather_ai_graph.invoke({
        "question": question,
        "default_latitude": default_latitude,
        "default_longitude": default_longitude,
        "default_location_name": default_location_name,
        "extracted_city": None,
        "latitude": default_latitude,
        "longitude": default_longitude,
        "location_name": default_location_name,
        "weather": {},
        "wants_earthquake": False,
        "earthquakes": [],
        "answer": "",
    })

    return {
        "answer": result["answer"],
        "resolved_location": result["location_name"],
        "extracted_city": result.get("extracted_city"),
        "wants_earthquake": result.get("wants_earthquake", False),
        "earthquake_count": len(result.get("earthquakes", [])),
    }
    