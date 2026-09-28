from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_licoes_tools(mcp: FastMCP, container: Container) -> None:
    service, audit = container.licoes, container.audit

    @mcp.tool(name="licoes_criar", structured_output=True)
    def criar(id_ciclo: int, contexto: str, expectativa: str) -> dict[str, Any]:
        """Cria lição aprendida com evidências do ciclo, gera PDF e anexa ao ciclo."""
        context = get_request_context()
        return execute_tool(name="licoes_criar", audit=audit, minimum_access="create",
                            operation=lambda: service.criar(context, id_ciclo=id_ciclo, contexto=contexto, expectativa=expectativa))

    @mcp.tool(name="licoes_resumir", structured_output=True)
    def resumir(id_ciclo: int | None = None) -> dict[str, Any]:
        """Resume lições aprendidas da empresa ou de um ciclo autorizado."""
        context = get_request_context()
        return execute_tool(name="licoes_resumir", audit=audit,
                            operation=lambda: service.resumir(context, id_ciclo=id_ciclo))

    @mcp.tool(name="licoes_perguntar", structured_output=True)
    def perguntar(id_ciclo: int, pergunta: str) -> dict[str, Any]:
        """Responde uma pergunta com lições do ciclo e retorna as referências usadas."""
        context = get_request_context()
        return execute_tool(name="licoes_perguntar", audit=audit,
                            operation=lambda: service.perguntar(context, id_ciclo=id_ciclo, pergunta=pergunta))
