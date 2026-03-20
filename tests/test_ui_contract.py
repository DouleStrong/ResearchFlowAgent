from pathlib import Path

from starlette.routing import Mount

from agent_api import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_ui_routes_are_registered():
    route_paths = [getattr(route, "path", None) for route in app.routes]

    assert "/ui" in route_paths
    assert any(isinstance(route, Mount) and route.path == "/static" for route in app.routes)


def test_ui_assets_include_streaming_and_hitl_hooks():
    ui_dir = PROJECT_ROOT / "ui"
    html = (ui_dir / "index.html").read_text(encoding="utf-8")
    js = (ui_dir / "app.js").read_text(encoding="utf-8")
    css = (ui_dir / "styles.css").read_text(encoding="utf-8")

    assert 'id="research-form"' in html
    assert 'id="interrupt-panel"' in html
    assert "ask/stream" in js
    assert "intervene/stream" in js
    assert "approve" in js
    assert "--surface" in css


def test_ui_assets_include_portfolio_storytelling_hooks():
    ui_dir = PROJECT_ROOT / "ui"
    html = (ui_dir / "index.html").read_text(encoding="utf-8")
    js = (ui_dir / "app.js").read_text(encoding="utf-8")
    css = (ui_dir / "styles.css").read_text(encoding="utf-8")

    assert "hero-metrics" in html
    assert "capability-grid" in html
    assert "workflow-list" in html
    assert 'id="hero-stage"' in html
    assert 'id="metric-token-count"' in html

    assert "metricTokenCount" in js
    assert "metricSourceCount" in js
    assert "setStageLabel" in js

    assert "--spotlight" in css
    assert "--paper" in css
    assert "--night-ink" in css
