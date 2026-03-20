from utils.models import ResearchReport


def test_research_report_schema_requires_sources():
    payload = {
        "summary": "这是一个测试摘要",
        "steps": ["检索资料", "对比方案"],
        "sources": [{"title": "Demo", "url": "https://example.com", "note": "示例来源"}],
        "next_actions": ["继续验证价格信息"],
    }

    report = ResearchReport(**payload)

    assert report.sources[0].title == "Demo"
