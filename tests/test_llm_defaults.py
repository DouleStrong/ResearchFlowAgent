import importlib
import logging
import sys
import types


def _install_fake_langchain_openai() -> None:
    fake_module = types.ModuleType("langchain_openai")

    class ChatOpenAI:
        pass

    class OpenAIEmbeddings:
        pass

    fake_module.ChatOpenAI = ChatOpenAI
    fake_module.OpenAIEmbeddings = OpenAIEmbeddings
    sys.modules["langchain_openai"] = fake_module


def _install_fake_concurrent_log_handler() -> None:
    fake_module = types.ModuleType("concurrent_log_handler")

    class ConcurrentRotatingFileHandler(logging.Handler):
        def __init__(self, *args, **kwargs):
            super().__init__()

    fake_module.ConcurrentRotatingFileHandler = ConcurrentRotatingFileHandler
    sys.modules["concurrent_log_handler"] = fake_module


def test_openai_provider_config_requires_env_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    sys.modules.pop("utils.llms", None)
    _install_fake_langchain_openai()
    _install_fake_concurrent_log_handler()

    llms = importlib.import_module("utils.llms")

    assert llms._read_provider_config("openai")["api_key"] == ""
