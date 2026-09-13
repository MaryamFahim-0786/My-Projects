from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_core.tools import Tool
import numexpr


def _calculate(expression: str) -> str:
    try:
        result = numexpr.evaluate(expression).item()
        return str(result)
    except Exception as exc:  # noqa: BLE001
        return f"Could not evaluate expression: {exc}"


def get_tools() -> list[Tool]:
    """Base tool set for the agent: live web search + a safe calculator.
    Add more Tool(...) entries here for custom API/DB integrations."""
    search = DuckDuckGoSearchRun(api_wrapper=DuckDuckGoSearchAPIWrapper(max_results=5))

    return [
        Tool(
            name="web_search",
            func=search.run,
            description="Use this to search the web for current events, facts, or anything you're unsure about.",
        ),
        Tool(
            name="calculator",
            func=_calculate,
            description="Use this to evaluate math expressions, e.g. '12 * (7 + 3)'.",
        ),
    ]
