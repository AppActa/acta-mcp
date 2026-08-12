from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_relatorio_tools(mcp: FastMCP, container: Container) -> None:
    service = container.relatorios
    audit = container.audit

    @mcp.tool(name="relatorios_contexto_ciclo", structured_output=True)
    def relatorios_contexto_ciclo(
        id_ciclo: int,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Lê e consolida evidências atuais para produzir um relatório do ciclo."""
        context = get_request_context()
        return execute_tool(
            name="relatorios_contexto_ciclo",
            audit=audit,
            minimum_access="geral",
            operation=lambda: service.contexto_ciclo(
                context,
                id_ciclo=id_ciclo,
                limit=limit,
            ),
        )
