from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_relatorio_tools(mcp: FastMCP, container: Container) -> None:
    service = container.relatorios
    audit = container.audit

    @mcp.tool(name="relatorios_listar", structured_output=True)
    def relatorios_listar(
        id_ciclo: int,
        tipo: str | None = None,
        formato: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Lista metadados dos relatórios persistidos e autorizados de um ciclo."""
        context = get_request_context()
        return execute_tool(
            name="relatorios_listar",
            audit=audit,
            operation=lambda: service.listar(
                context,
                id_ciclo=id_ciclo,
                tipo=tipo,
                formato=formato,
                status=status,
                limit=limit,
            ),
        )

    @mcp.tool(name="relatorios_detalhes", structured_output=True)
    def relatorios_detalhes(id_ciclo: int, id_relatorio: str) -> dict[str, Any]:
        """Obtém metadados e conteúdo de um relatório autorizado."""
        context = get_request_context()
        return execute_tool(
            name="relatorios_detalhes",
            audit=audit,
            operation=lambda: service.detalhes(
                context,
                id_ciclo=id_ciclo,
                id_relatorio=id_relatorio,
            ),
        )

    @mcp.tool(name="relatorios_mais_recente", structured_output=True)
    def relatorios_mais_recente(
        id_ciclo: int,
        tipo: str | None = None,
    ) -> dict[str, Any]:
        """Obtém o relatório mais recente do ciclo, opcionalmente por tipo."""
        context = get_request_context()
        return execute_tool(
            name="relatorios_mais_recente",
            audit=audit,
            operation=lambda: service.mais_recente(
                context,
                id_ciclo=id_ciclo,
                tipo=tipo,
            ),
        )

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
            operation=lambda: service.contexto_ciclo(
                context,
                id_ciclo=id_ciclo,
                limit=limit,
            ),
        )
