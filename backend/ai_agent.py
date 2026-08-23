import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from typing import TypedDict


load_dotenv()


# ============================================================
# STATE
# ============================================================

class WeatherAIState(TypedDict):
    question: str
    weather_context: str
    answer: str


# ============================================================
# GROQ MODEL (via OpenAI-compatible endpoint)
# ============================================================

llm = ChatOpenAI(
    model="openai/gpt-oss-20b",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)


# ============================================================
# AI NODE
# ============================================================

def generate_answer(state: WeatherAIState):

    question = state["question"]
    weather_context = state["weather_context"]

    prompt = f"""
You are an AI Weather Assistant.

Answer the user's weather question clearly and naturally.

Weather information:
{weather_context}

User question:
{question}

Rules:
- Use the provided weather information.
- Do not invent weather data.
- Keep the answer easy to understand.
- If the weather information is insufficient, say so.
- Give practical advice when appropriate.
"""

    response = llm.invoke(prompt)

    return {
        "answer": response.content
    }


# ============================================================
# LANGGRAPH
# ============================================================

graph_builder = StateGraph(WeatherAIState)

graph_builder.add_node(
    "generate_answer",
    generate_answer,
)

graph_builder.add_edge(
    START,
    "generate_answer",
)

graph_builder.add_edge(
    "generate_answer",
    END,
)

weather_ai_graph = graph_builder.compile()


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def ask_weather_ai(
    question: str,
    weather_context: str,
) -> str:

    result = weather_ai_graph.invoke(
        {
            "question": question,
            "weather_context": weather_context,
            "answer": "",
        }
    )

    return result["answer"]