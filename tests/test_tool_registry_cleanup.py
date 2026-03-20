import asyncio

from utils.tools import get_tools


def test_get_tools_only_registers_research_scope(monkeypatch):
    captured = {}

    class DummyTool:
        def __init__(self, name):
            self.name = name

    class FakeMCPClient:
        def __init__(self, servers):
            captured["servers"] = servers

        async def get_tools(self):
            return [DummyTool("search_documents")]

    class FakeHITLMiddleware:
        def __init__(self, interrupt_on, description_prefix):
            captured["interrupt_on"] = interrupt_on
            captured["description_prefix"] = description_prefix

    monkeypatch.setattr("utils.tools.MultiServerMCPClient", FakeMCPClient)
    monkeypatch.setattr("utils.tools.HumanInTheLoopMiddleware", FakeHITLMiddleware)

    tools, _middleware = asyncio.run(get_tools())
    tool_names = [tool.name for tool in tools]

    assert "search_documents" in tool_names
    assert "build_research_outline" in tool_names
    assert "save_markdown_report" in tool_names
    assert "remember_user_preference" in tool_names

    assert "load_skill" not in tool_names
    assert "run_skill_python" not in tool_names
    assert "get_weather_for_location" not in tool_names
    assert "get_user_location" not in tool_names

    assert "search_documents" in captured["interrupt_on"]
    assert "load_skill" not in captured["interrupt_on"]
    assert "run_skill_python" not in captured["interrupt_on"]
