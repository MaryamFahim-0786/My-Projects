"""
Sanity tests for the portfolio knowledge base (app/data/).

These guard against two easy mistakes when personalising the template:
  1. leaving the previous owner's identity in the data the chatbot reads, and
  2. losing the automatic re-index behaviour when the data changes.
"""
import re
from pathlib import Path

from langchain.docstore.document import Document

from app.services.rag_service import _content_fingerprint

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data"

# Identity details of the original template author that must not remain in
# the knowledge base. (portfolio.txt is allowed to mention "Roy Amit" once,
# purely as honest attribution for the open-source template.)
FORBIDDEN = re.compile(
    r"royamit|bar-ilan|\bcommit\b|\.net maui|tank commander|\bidf\b|"
    r"space ?ease|yeet|arkanoid|knn classifier|news broadcasting",
    re.IGNORECASE,
)


def _data_files():
    return sorted(DATA_DIR.rglob("*.txt"))


def test_knowledge_base_files_exist():
    names = {p.name for p in _data_files()}
    assert {"personal_background.txt", "linkedin_summary.txt", "resume_summary.txt"} <= names
    assert len(list((DATA_DIR / "projects").glob("*.txt"))) >= 5


def test_no_previous_owner_details_in_data():
    for path in _data_files():
        text = path.read_text(encoding="utf-8")
        assert not FORBIDDEN.search(text), f"Old-owner content found in {path.name}"


def test_previous_owner_name_only_appears_as_attribution():
    for path in _data_files():
        text = path.read_text(encoding="utf-8")
        if path.name != "portfolio.txt":
            assert "Roy" not in text, f"'Roy' found in {path.name}"


def test_every_file_is_about_the_new_owner():
    for path in (DATA_DIR / "projects").glob("*.txt"):
        assert "Maryam Fahim" in path.read_text(encoding="utf-8"), path.name


def test_fingerprint_is_stable_and_order_independent():
    a = Document(page_content="alpha")
    b = Document(page_content="beta")
    assert _content_fingerprint([a, b]) == _content_fingerprint([b, a])


def test_fingerprint_changes_when_content_changes():
    before = _content_fingerprint([Document(page_content="alpha")])
    after = _content_fingerprint([Document(page_content="alpha edited")])
    assert before != after
