import asyncio

from rag_mcp.rag_mcp_server import call_tool


def test_search_documents_returns_source_fields(monkeypatch):
    class FakeEntity:
        def __init__(self):
            self.payload = {
                "title": "Claude Code 与 Cursor 的使用场景比较",
                "content_chunk": "Claude Code 更适合终端协作和代码库导航，Cursor 更适合 IDE 内联编辑。",
                "link": "https://example.com/claude-code-vs-cursor",
                "pubAuthor": "ResearchFlow",
                "pubDate": "2026-03-18",
            }

        def get(self, key, default=""):
            return self.payload.get(key, default)

    class FakeResult:
        entity = FakeEntity()
        distance = 0.12

    class FakeSearchManager:
        def __init__(self, milvus_uri, db_name):
            self.milvus_uri = milvus_uri
            self.db_name = db_name

        def search_with_filter(self, collection_name, query_text, filter_query, search_type, limit):
            return {
                "success": True,
                "total_results": 1,
                "results": [[FakeResult()]],
            }

    monkeypatch.setattr("rag_mcp.rag_mcp_server.MilvusSearchManager", FakeSearchManager)

    result = asyncio.run(
        call_tool(
            "search_documents",
            {
                "query_text": "AI Coding 工具对比",
                "filter_query": "##None##",
                "search_type": "hybrid",
                "limit": 2,
            },
        )
    )

    text = result[0].text
    assert "文章标题:" in text
    assert "文章原始链接:" in text
    assert "文章发布者:" in text
    assert "文章发布时间:" in text
    assert "文章内容片段:" in text
