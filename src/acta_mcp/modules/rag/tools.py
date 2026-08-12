from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_rag_tools(mcp: FastMCP, container: Container) -> None:
    @mcp.tool(name="faq_retriever", structured_output=True)
    def faq_retriever(question: str, limit: int = 3) -> dict[str, Any]:
        """Busca trechos conceituais sobre ACTA, PDCA e ferramentas de qualidade."""
        get_request_context()
        return execute_tool(
            name="faq_retriever",
            audit=container.audit,
            operation=lambda: container.rag.search(question, limit),
        )
