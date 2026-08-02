from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_skill_tools(mcp: FastMCP, container: Container) -> None:
    service = container.skills
    audit = container.audit

    @mcp.tool(name="skills_criar", structured_output=True)
    def criar(conteudo_markdown: str) -> dict[str, Any]:
        """Cria ou atualiza uma skill segura usando somente nome, objetivo e regras."""
        context = get_request_context()
        return execute_tool(
            name="skills_criar",
            audit=audit,
            operation=lambda: service.criar(context, conteudo_markdown=conteudo_markdown),
        )

    @mcp.tool(name="skills_obter", structured_output=True)
    def obter(nome: str) -> dict[str, Any]:
        """Obtém uma skill do usuário autenticado pelo nome ou comando."""
        context = get_request_context()
        return execute_tool(
            name="skills_obter",
            audit=audit,
            operation=lambda: service.obter(context, nome=nome),
        )

    @mcp.tool(name="skills_listar", structured_output=True)
    def listar(limit: int = 50) -> dict[str, Any]:
        """Lista os comandos de skills do usuário autenticado."""
        context = get_request_context()
        return execute_tool(
            name="skills_listar",
            audit=audit,
            operation=lambda: service.listar(context, limit=limit),
        )

    @mcp.tool(name="skills_excluir", structured_output=True)
    def excluir(nome: str) -> dict[str, Any]:
        """Exclui uma skill do usuário autenticado."""
        context = get_request_context()
        return execute_tool(
            name="skills_excluir",
            audit=audit,
            operation=lambda: service.excluir(context, nome=nome),
        )

