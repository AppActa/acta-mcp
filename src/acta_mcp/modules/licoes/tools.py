from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_licoes_tools(mcp: FastMCP, container: Container) -> None:
    service = container.licoes

    @mcp.tool(name="licoes_listar_entre_ciclos", structured_output=True)
    def listar_entre_ciclos(limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """Lista lições nos ciclos autorizados do usuário, com id_ciclo em cada resultado."""
        context = get_request_context()
        return execute_tool(operation=lambda: service.listar_entre_ciclos(
            context, limit=limit, offset=offset
        ))

    @mcp.tool(name="licoes_resumir_entre_ciclos", structured_output=True)
    def resumir_entre_ciclos(limit: int = 200) -> dict[str, Any]:
        """Resume lições dos ciclos autorizados do usuário e retorna referências por ciclo."""
        context = get_request_context()
        return execute_tool(operation=lambda: service.resumir_entre_ciclos(context, limit=limit))

    @mcp.tool(name="licoes_perguntar_entre_ciclos", structured_output=True)
    def perguntar_entre_ciclos(pergunta: str, limit: int = 200) -> dict[str, Any]:
        """Responde perguntas com lições dos ciclos autorizados, preservando referências por ciclo."""
        context = get_request_context()
        return execute_tool(operation=lambda: service.perguntar_entre_ciclos(
            context, pergunta=pergunta, limit=limit
        ))

    @mcp.tool(name="licoes_criar", structured_output=True)
    def criar(id_ciclo: int, contexto: str, expectativa: str) -> dict[str, Any]:
        """Cria lição aprendida com evidências do ciclo, gera PDF e anexa ao ciclo."""
        context = get_request_context()
        return execute_tool(minimum_access="create",
                            operation=lambda: service.criar(context, id_ciclo=id_ciclo, contexto=contexto, expectativa=expectativa))

    @mcp.tool(name="licoes_resumir", structured_output=True)
    def resumir(id_ciclo: int) -> dict[str, Any]:
        """Resume lições aprendidas do ciclo autorizado."""
        context = get_request_context()
        return execute_tool(
                            operation=lambda: service.resumir(context, id_ciclo=id_ciclo))

    @mcp.tool(name="licoes_perguntar", structured_output=True)
    def perguntar(id_ciclo: int, pergunta: str) -> dict[str, Any]:
        """Responde uma pergunta com lições do ciclo e retorna as referências usadas."""
        context = get_request_context()
        return execute_tool(
                            operation=lambda: service.perguntar(context, id_ciclo=id_ciclo, pergunta=pergunta))
