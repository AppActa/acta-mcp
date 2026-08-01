from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_formulario_tools(mcp: FastMCP, container: Container) -> None:
    service = container.formularios
    audit = container.audit

    @mcp.tool(name="formularios_listar", structured_output=True)
    def formularios_listar(
        id_ciclo: int,
        id_formulario: str | None = None,
        tipo: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Lista formulários autorizados do ciclo com filtros opcionais."""
        context = get_request_context()
        return execute_tool(
            name="formularios_listar",
            audit=audit,
            operation=lambda: service.listar(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
                tipo=tipo,
                status=status,
                limit=limit,
            ),
        )

    @mcp.tool(name="formularios_detalhes", structured_output=True)
    def formularios_detalhes(
        id_ciclo: int,
        id_formulario: str,
        limit_respostas: int = 100,
    ) -> dict[str, Any]:
        """Obtém a definição de um formulário e suas respostas autorizadas."""
        context = get_request_context()
        return execute_tool(
            name="formularios_detalhes",
            audit=audit,
            operation=lambda: service.detalhes(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
                limit_respostas=limit_respostas,
            ),
        )

    @mcp.tool(name="formularios_respostas", structured_output=True)
    def formularios_respostas(
        id_ciclo: int,
        id_formulario: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Consulta respostas de formulários autorizadas para o ciclo."""
        context = get_request_context()
        return execute_tool(
            name="formularios_respostas",
            audit=audit,
            operation=lambda: service.respostas(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
                limit=limit,
            ),
        )

    @mcp.tool(name="formularios_resumo_respostas", structured_output=True)
    def formularios_resumo_respostas(
        id_ciclo: int,
        id_formulario: str | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        """Consolida respostas, frequências e padrões repetidos dos formulários."""
        context = get_request_context()
        return execute_tool(
            name="formularios_resumo_respostas",
            audit=audit,
            operation=lambda: service.resumo_respostas(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
                limit=limit,
            ),
        )
