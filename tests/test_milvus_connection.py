import os

from utils.milvus_connection import create_milvus_client


def test_create_milvus_client_temporarily_disables_proxy_for_local_uri(monkeypatch):
    captured = {}

    class DummyMilvusClient:
        def __init__(self, **kwargs):
            captured["kwargs"] = kwargs
            captured["http_proxy_during_init"] = os.environ.get("HTTP_PROXY")
            captured["http_proxy_lower_during_init"] = os.environ.get("http_proxy")
            captured["no_proxy_during_init"] = os.environ.get("NO_PROXY")
            captured["no_proxy_lower_during_init"] = os.environ.get("no_proxy")

    monkeypatch.setattr("utils.milvus_connection.MilvusClient", DummyMilvusClient)
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:7890")
    monkeypatch.setenv("http_proxy", "http://127.0.0.1:7890")
    monkeypatch.setenv("NO_PROXY", "example.com")
    monkeypatch.setenv("no_proxy", "example.com")

    create_milvus_client(
        uri="http://127.0.0.1:19530",
        db_name="milvus_database",
        timeout=30,
    )

    assert captured["kwargs"]["uri"] == "http://127.0.0.1:19530"
    assert captured["kwargs"]["db_name"] == "milvus_database"
    assert captured["kwargs"]["timeout"] == 30
    assert "channel" not in captured["kwargs"]
    assert captured["http_proxy_during_init"] == ""
    assert captured["http_proxy_lower_during_init"] == ""
    assert "127.0.0.1" in captured["no_proxy_during_init"]
    assert "localhost" in captured["no_proxy_during_init"]
    assert "127.0.0.1" in captured["no_proxy_lower_during_init"]
    assert "localhost" in captured["no_proxy_lower_during_init"]
    assert os.environ["HTTP_PROXY"] == "http://127.0.0.1:7890"
    assert os.environ["http_proxy"] == "http://127.0.0.1:7890"
