from typing import Any, Literal

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
            minimum_access="geral",
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
            minimum_access="geral",
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
            minimum_access="geral",
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
            minimum_access="geral",
            operation=lambda: service.resumo_respostas(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
                limit=limit,
            ),
        )

    @mcp.tool(name="formularios_criar_rascunho", structured_output=True)
    def formularios_criar_rascunho(
        id_ciclo: int,
        titulo: str,
        tipo: str,
        descricao: str | None = None,
    ) -> dict[str, Any]:
        """Cria um formulário em rascunho; exige acesso geral."""
        context = get_request_context()
        return execute_tool(
            name="formularios_criar_rascunho",
            audit=audit,
            minimum_access="geral",
            operation=lambda: service.criar_rascunho(
                context,
                id_ciclo=id_ciclo,
                titulo=titulo,
                tipo=tipo,
                descricao=descricao,
            ),
        )

    @mcp.tool(name="formularios_adicionar_pergunta", structured_output=True)
    def formularios_adicionar_pergunta(
        id_ciclo: int,
        id_formulario: str,
        texto: str,
        tipo_resposta: Literal[
            "TEXTO", "NUMERO", "DATA", "BOOLEANO", "SELECAO_UNICA", "MULTIPLA"
        ],
        obrigatoria: bool = False,
        opcoes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Adiciona uma pergunta estruturada a um formulário rascunho."""
        context = get_request_context()
        return execute_tool(
            name="formularios_adicionar_pergunta",
            audit=audit,
            minimum_access="geral",
            operation=lambda: service.adicionar_pergunta(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
                texto=texto,
                tipo_resposta=tipo_resposta,
                obrigatoria=obrigatoria,
                opcoes=opcoes or [],
            ),
        )

    @mcp.tool(name="formularios_publicar", structured_output=True)
    def formularios_publicar(id_ciclo: int, id_formulario: str) -> dict[str, Any]:
        """Publica um formulário autorizado que possua ao menos uma pergunta."""
        context = get_request_context()
        return execute_tool(
            name="formularios_publicar",
            audit=audit,
            minimum_access="geral",
            operation=lambda: service.publicar(
                context,
                id_ciclo=id_ciclo,
                id_formulario=id_formulario,
            ),
        )
