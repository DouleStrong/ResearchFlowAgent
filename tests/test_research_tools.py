import json
from pathlib import Path

from utils.research_tools import (
    build_research_outline,
    remember_user_preference,
    save_markdown_report,
)


def test_build_research_outline_has_required_sections():
    outline = build_research_outline(topic="AI Coding 工具", audience="产品经理")

    assert outline["topic"] == "AI Coding 工具"
    assert outline["audience"] == "产品经理"
    assert "市场概览" in outline["sections"]
    assert "建议行动" in outline["sections"]


def test_save_markdown_report_writes_file(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORTS_DIR", str(tmp_path))

    path = Path(save_markdown_report("tool-landscape", "# demo"))

    assert path.suffix == ".md"
    assert path.exists()
    assert path.read_text(encoding="utf-8") == "# demo"


def test_remember_user_preference_persists_to_json(tmp_path, monkeypatch):
    monkeypatch.setenv("PREFERENCES_DIR", str(tmp_path))

    result = remember_user_preference("tone", "structured", user_id="user_001")
    stored_path = Path(result["path"])

    assert result["status"] == "stored"
    assert stored_path.exists()

    payload = json.loads(stored_path.read_text(encoding="utf-8"))
    assert payload["user_id"] == "user_001"
    assert payload["preferences"]["tone"] == "structured"
