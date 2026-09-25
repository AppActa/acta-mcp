from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.tooling import execute_tool


def register_faq_tools(mcp: FastMCP, container: Container) -> None:
    service, audit = container.faq, container.audit

    @mcp.tool(name="faq_retriever", structured_output=True)
    def faq_retriever(question: str, limit: int = 3) -> dict[str, Any]:
        """Busca trechos da documentação ACTA, PDCA e ferramentas da qualidade."""
        return execute_tool(
            name="faq_retriever",
            audit=audit,
            operation=lambda: service.search(question, limit),
        )
