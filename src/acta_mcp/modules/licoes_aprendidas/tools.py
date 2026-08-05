from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_licoes_aprendidas_tools(mcp: FastMCP, container: Container) -> None:
    service = container.licoes_aprendidas
    audit = container.audit

    @mcp.tool(name="licoes_aprendidas_registrar", structured_output=True)
    def registrar(
        id_ciclo: int,
        titulo: str,
        licao: str,
        categoria: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Registra uma lição aprendida em um ciclo autorizado."""
        context = get_request_context()
        return execute_tool(
            name="licoes_aprendidas_registrar",
            audit=audit,
            minimum_access="create",
            operation=lambda: service.registrar(
                context,
                id_ciclo=id_ciclo,
                titulo=titulo,
                licao=licao,
                categoria=categoria,
                tags=tags or [],
            ),
        )

