from datetime import date
from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_treinamento_tools(mcp: FastMCP, container: Container) -> None:
    service = container.treinamentos
    audit = container.audit

    @mcp.tool(name="treinamentos_criar", structured_output=True)
    def criar(
        id_ciclo: int,
        id_responsavel: int,
        titulo: str,
        data_treinamento: date,
        descricao: str | None = None,
        obrigatorio: bool = True,
        participantes: list[int] | None = None,
    ) -> dict[str, Any]:
        """Cria um treinamento e vincula participantes autorizados; exige acesso geral."""
        context = get_request_context()
        return execute_tool(
            name="treinamentos_criar",
            audit=audit,
            minimum_access="geral",
            operation=lambda: service.criar(
                context,
                id_ciclo=id_ciclo,
                id_responsavel=id_responsavel,
                titulo=titulo,
                descricao=descricao,
                data_treinamento=data_treinamento,
                obrigatorio=obrigatorio,
                participantes=participantes or [],
            ),
        )

