import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parents[1]

    PROJECT_NAME = os.getenv("PROJECT_NAME", "ResearchFlow Agent")
    REPORTS_DIR = os.getenv("REPORTS_DIR", str(BASE_DIR / "reports"))
    PREFERENCES_DIR = os.getenv("PREFERENCES_DIR", str(BASE_DIR / "preferences"))
    DEFAULT_USER_ID = os.getenv("DEFAULT_USER_ID", "user_001")

    LOG_FILE = str(BASE_DIR / "logfile" / "researchflow_agent.log")
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    MAX_BYTES = 5 * 1024 * 1024
    BACKUP_COUNT = 3

    DB_URI = os.getenv(
        "DB_URI",
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres?sslmode=disable",
    )
    MIN_SIZE = int(os.getenv("DB_POOL_MIN_SIZE", "5"))
    MAX_SIZE = int(os.getenv("DB_POOL_MAX_SIZE", "10"))

    LLM_TYPE = os.getenv("LLM_TYPE", "openai")
    SYSTEM_PROMPT_TMPL = os.getenv("SYSTEM_PROMPT_TMPL", "prompt/system_prompt_tmpl.md")
    HUMAN_PROMPT_TMPL = os.getenv("HUMAN_PROMPT_TMPL", "prompt/human_prompt_tmpl.md")

    MILVUS_URI = os.getenv("MILVUS_URI", "http://127.0.0.1:19530")
    MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "milvus_database")
    MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "my_collection_demo_chunked")

    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8010"))

    API_SERVER_HOST = os.getenv("API_SERVER_HOST", "0.0.0.0")
    API_SERVER_PORT = int(os.getenv("API_SERVER_PORT", "8202"))
    API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8202")
