import json
import os
import re
from pathlib import Path

from .config import Config


_SAFE_SEGMENT = re.compile(r"[^a-zA-Z0-9_-]+")


def _safe_segment(value: str, fallback: str) -> str:
    cleaned = _SAFE_SEGMENT.sub("-", value).strip("-")
    return cleaned or fallback


def build_research_outline(topic: str, audience: str) -> dict:
    normalized_topic = topic.strip()
    normalized_audience = audience.strip() or "通用读者"
    return {
        "topic": normalized_topic,
        "audience": normalized_audience,
        "sections": ["问题定义", "市场概览", "关键信号", "方案比较", "建议行动"],
    }


def save_markdown_report(title: str, content: str) -> str:
    reports_dir = Path(os.getenv("REPORTS_DIR", Config.REPORTS_DIR))
    reports_dir.mkdir(parents=True, exist_ok=True)

    safe_title = _safe_segment(title, "report")
    path = reports_dir / f"{safe_title}.md"
    path.write_text(content, encoding="utf-8")
    return str(path)


def remember_user_preference(key: str, value: str, user_id: str = Config.DEFAULT_USER_ID) -> dict:
    preferences_dir = Path(
        os.getenv("PREFERENCES_DIR", str(Config.BASE_DIR / "preferences"))
    )
    preferences_dir.mkdir(parents=True, exist_ok=True)

    safe_user_id = _safe_segment(user_id, "user")
    path = preferences_dir / f"{safe_user_id}.json"

    payload = {"user_id": user_id, "preferences": {}}
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))

    payload.setdefault("user_id", user_id)
    payload.setdefault("preferences", {})
    payload["preferences"][key] = value
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "status": "stored",
        "path": str(path),
        "user_id": user_id,
        "key": key,
        "value": value,
    }
