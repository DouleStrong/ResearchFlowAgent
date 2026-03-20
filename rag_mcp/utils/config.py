import os
from pathlib import Path


class Config:
    BASE_DIR = Path(__file__).resolve().parents[1]

    LOG_FILE = str(BASE_DIR / "logfile" / "rag_mcp.log")
    Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
    MAX_BYTES = 5 * 1024 * 1024
    BACKUP_COUNT = 3

    LLM_TYPE = os.getenv("LLM_TYPE", "openai")

    MILVUS_URI = os.getenv("MILVUS_URI", "http://127.0.0.1:19530")
    MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "milvus_database")
    MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "my_collection_demo_chunked")

    MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
    MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8010"))
