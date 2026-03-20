import os

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from .logger import LoggerManager


logger = LoggerManager.get_logger()

DEFAULT_LLM_TYPE = os.getenv("LLM_TYPE", "openai")
DEFAULT_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0"))
DEFAULT_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))
DEFAULT_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))


class LLMInitializationError(Exception):
    pass


def _read_provider_config(llm_type: str) -> dict:
    if llm_type == "openai":
        return {
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", ""),
            "chat_model": os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini"),
            "embedding_model": os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        }
    if llm_type == "qwen":
        return {
            "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
            "api_key": os.getenv("QWEN_API_KEY", ""),
            "chat_model": os.getenv("QWEN_CHAT_MODEL", "qwen-turbo-latest"),
            "embedding_model": os.getenv("QWEN_EMBEDDING_MODEL", "text-embedding-v1"),
        }
    if llm_type == "oneapi":
        return {
            "base_url": os.getenv("ONEAPI_BASE_URL", "http://127.0.0.1:3000/v1"),
            "api_key": os.getenv("ONEAPI_API_KEY", ""),
            "chat_model": os.getenv("ONEAPI_CHAT_MODEL", "qwen-max"),
            "embedding_model": os.getenv("ONEAPI_EMBEDDING_MODEL", "text-embedding-v1"),
        }
    if llm_type == "ollama":
        return {
            "base_url": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1"),
            "api_key": os.getenv("OLLAMA_API_KEY", "ollama"),
            "chat_model": os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b"),
            "embedding_model": os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
        }
    raise ValueError(f"不支持的 LLM 类型: {llm_type}")


def _validate_provider_config(llm_type: str, config: dict) -> None:
    required_keys = ["base_url", "chat_model", "embedding_model"]
    if llm_type != "ollama":
        required_keys.append("api_key")

    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        raise ValueError(f"{llm_type} 配置缺少必要字段: {', '.join(missing)}")


def initialize_llm(llm_type: str = DEFAULT_LLM_TYPE) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    try:
        config = _read_provider_config(llm_type)
        _validate_provider_config(llm_type, config)

        llm_chat = ChatOpenAI(
            base_url=config["base_url"],
            api_key=config["api_key"],
            model=config["chat_model"],
            temperature=DEFAULT_TEMPERATURE,
            timeout=DEFAULT_TIMEOUT,
            max_retries=DEFAULT_MAX_RETRIES,
        )

        llm_embedding = OpenAIEmbeddings(
            base_url=config["base_url"],
            api_key=config["api_key"],
            model=config["embedding_model"],
        )

        logger.info("成功初始化 %s LLM", llm_type)
        return llm_chat, llm_embedding
    except ValueError as exc:
        logger.error("LLM 配置错误: %s", exc)
        raise LLMInitializationError(f"LLM 配置错误: {exc}") from exc
    except Exception as exc:
        logger.error("初始化 LLM 失败: %s", exc)
        raise LLMInitializationError(f"初始化 LLM 失败: {exc}") from exc


def get_llm(llm_type: str = DEFAULT_LLM_TYPE) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    try:
        return initialize_llm(llm_type)
    except LLMInitializationError as exc:
        logger.warning("使用默认配置重试: %s", exc)
        if llm_type != DEFAULT_LLM_TYPE:
            return initialize_llm(DEFAULT_LLM_TYPE)
        raise
