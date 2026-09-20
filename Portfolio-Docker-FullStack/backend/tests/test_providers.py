"""Tests for switching the chatbot between OpenAI and Gemini (LLM_PROVIDER)."""
import os
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.services.agent_service import _chunk_text

BACKEND_DIR = Path(__file__).resolve().parent.parent
BASE = {"RESEND_API_KEY": "re_test", "OWNER_EMAIL": "owner@example.com"}


@pytest.fixture(autouse=True)
def clean_provider_env(monkeypatch):
    """Keys/provider set in the developer's shell or CI must not leak into these tests."""
    for name in ("LLM_PROVIDER", "OPENAI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(name, raising=False)


def make(**kw):
    # _env_file=None so a developer's real backend/.env can't influence the test
    return Settings(_env_file=None, **{**BASE, **kw})


def test_default_provider_is_openai_and_needs_openai_key():
    assert make(OPENAI_API_KEY="sk-test").LLM_PROVIDER == "openai"
    with pytest.raises(ValidationError, match="OPENAI_API_KEY"):
        make()


def test_gemini_requires_google_key():
    with pytest.raises(ValidationError, match="GOOGLE_API_KEY"):
        make(LLM_PROVIDER="gemini")
    with pytest.raises(ValidationError, match="GOOGLE_API_KEY"):
        make(LLM_PROVIDER="gemini", GOOGLE_API_KEY="   ")


def test_gemini_with_key_and_provider_is_case_insensitive():
    s = make(LLM_PROVIDER=" Gemini ", GOOGLE_API_KEY="g-test")
    assert s.LLM_PROVIDER == "gemini"
    assert s.GEMINI_MODEL and s.GEMINI_EMBEDDING_MODEL.startswith("models/")


def test_unknown_provider_rejected():
    with pytest.raises(ValidationError, match="LLM_PROVIDER"):
        make(LLM_PROVIDER="claude", OPENAI_API_KEY="sk-test")


def test_chunk_text_handles_str_and_gemini_style_lists():
    assert _chunk_text("hello") == "hello"
    assert _chunk_text([{"type": "text", "text": "a"}, "b", {"type": "image"}]) == "ab"
    assert _chunk_text(None) == ""


def test_agent_builds_and_tools_convert_in_gemini_mode():
    """Runs the real app wiring in Gemini mode (offline, fake key) in a clean process."""
    code = (
        "import warnings; warnings.simplefilter('ignore')\n"
        "from langchain_core.messages import HumanMessage\n"
        "from app.services import agent_service as a\n"
        "assert type(a.llm).__name__ == 'ChatGoogleGenerativeAI', type(a.llm)\n"
        "bound = a.llm.bind_tools(a.tools)\n"
        "req = a.llm._prepare_request(messages=[HumanMessage(content='hi')], tools=bound.kwargs['tools'])\n"
        "names = sorted(d.name for t in req.tools for d in t.function_declarations)\n"
        "print('OK', names)\n"
    )
    env = {**os.environ, **BASE, "LLM_PROVIDER": "gemini", "GOOGLE_API_KEY": "fake",
           "RESEND_FROM": "t@example.com", "REDIS_HOST": "localhost", "POSTGRES_HOST": "localhost"}
    env.pop("OPENAI_API_KEY", None)
    out = subprocess.run([sys.executable, "-W", "ignore", "-c", code], cwd=BACKEND_DIR,
                         env=env, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-800:]
    assert "PortfolioKnowledgeBase" in out.stdout and "SendResumeEmail" in out.stdout
