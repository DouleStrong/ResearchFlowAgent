import json

from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import ToolRuntime, tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.config import get_stream_writer

from .config import Config
from .logger import LoggerManager
from .models import Context
from .research_tools import (
    build_research_outline as build_research_outline_impl,
    remember_user_preference as remember_user_preference_impl,
    save_markdown_report as save_markdown_report_impl,
)


logger = LoggerManager.get_logger()


def _build_mcp_server_url() -> str:
    host = Config.MCP_SERVER_HOST.rstrip("/")
    if host.startswith("http://") or host.startswith("https://"):
        return f"{host}/mcp"
    return f"http://{host}:{Config.MCP_SERVER_PORT}/mcp"


async def get_tools():
    @tool("build_research_outline", description="围绕研究主题生成结构化研究提纲。")
    async def build_research_outline(topic: str, audience: str = "通用读者") -> str:
        writer = get_stream_writer()
        writer(f"正在生成研究提纲: topic={topic}, audience={audience}")
        payload = build_research_outline_impl(topic=topic, audience=audience)
        return json.dumps(payload, ensure_ascii=False)

    @tool("save_markdown_report", description="将研究结论保存为 Markdown 报告并返回文件路径。")
    async def save_markdown_report(title: str, content: str) -> str:
        writer = get_stream_writer()
        writer(f"正在保存研究报告: {title}")
        path = save_markdown_report_impl(title=title, content=content)
        return json.dumps({"status": "saved", "path": path}, ensure_ascii=False)

    @tool("remember_user_preference", description="记录用户偏好，供后续研究任务复用。")
    async def remember_user_preference(key: str, value: str, runtime: ToolRuntime[Context]) -> str:
        writer = get_stream_writer()
        user_id = runtime.context.user_id
        writer(f"正在记录用户偏好: user_id={user_id}, {key}={value}")
        payload = remember_user_preference_impl(key=key, value=value, user_id=user_id)
        return json.dumps(payload, ensure_ascii=False)

    client = MultiServerMCPClient(
        {
            "rag_mcp_server": {
                "url": _build_mcp_server_url(),
                "transport": "streamable_http",
            }
        }
    )

    tools = list(await client.get_tools())
    tools.extend(
        [
            build_research_outline,
            save_markdown_report,
            remember_user_preference,
        ]
    )

    interrupt_on = {
        "search_documents": {
            "allowed_decisions": ["approve", "edit", "reject"],
            "description": "调用 search_documents 工具需要人工审批。请输入 approve、reject 或 edit。",
        }
    }

    hitl_middleware = HumanInTheLoopMiddleware(
        interrupt_on=interrupt_on,
        description_prefix="工具调用需要人工审批",
    )

    logger.info(
        "获取并提供的工具列表: %s",
        [getattr(tool_obj, "name", repr(tool_obj)) for tool_obj in tools],
    )
    logger.info("需要人工审批的工具有：%s", list(interrupt_on))

    return tools, hitl_middleware
