from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_colaborador_tools(mcp: FastMCP, container: Container) -> None:
    service = container.colaboradores
    audit = container.audit

    @mcp.tool(name="colaboradores_consultar", structured_output=True)
    def colaboradores_consultar(
        id_ciclo: int | None = None,
        nome: str | None = None,
        area: str | None = None,
        cargo: str | None = None,
        status: Literal["ATIVO", "INATIVO", "PENDENTE", "BLOQUEADO", "ARQUIVADO"] | None = None,
        tipo_usuario: Literal["ADMIN", "GESTOR", "COLABORADOR"] | None = None,
        permissao_gestor: bool | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Consulta colaboradores da empresa autenticada com filtros opcionais."""
        context = get_request_context()
        return execute_tool(
            name="colaboradores_consultar",
            audit=audit,
            operation=lambda: service.consultar(
                context,
                id_ciclo=id_ciclo,
                nome=nome,
                area=area,
                cargo=cargo,
                status=status,
                tipo_usuario=tipo_usuario,
                permissao_gestor=permissao_gestor,
                limit=limit,
            ),
        )

    @mcp.tool(name="colaborador_detalhes", structured_output=True)
    def colaborador_detalhes(
        id_colaborador: int,
        id_ciclo: int | None = None,
    ) -> dict[str, Any]:
        """Consulta detalhes profissionais e alocações de um colaborador autorizado."""
        context = get_request_context()
        return execute_tool(
            name="colaborador_detalhes",
            audit=audit,
            operation=lambda: service.detalhes(context, id_colaborador, id_ciclo),
        )

    @mcp.tool(name="colaboradores_participantes_ciclo", structured_output=True)
    def colaboradores_participantes_ciclo(
        id_ciclo: int,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Lista colaboradores participantes de um ciclo e seus papéis."""
        context = get_request_context()
        return execute_tool(
            name="colaboradores_participantes_ciclo",
            audit=audit,
            operation=lambda: service.participantes(context, id_ciclo, limit),
        )

    @mcp.tool(name="colaboradores_por_area", structured_output=True)
    def colaboradores_por_area() -> dict[str, Any]:
        """Agrupa colaboradores por área dentro da empresa autenticada."""
        context = get_request_context()
        return execute_tool(
            name="colaboradores_por_area",
            audit=audit,
            operation=lambda: service.por_area(context),
        )

    @mcp.tool(name="colaboradores_carga_trabalho", structured_output=True)
    def colaboradores_carga_trabalho(
        id_ciclo: int,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Calcula a carga de trabalho dos participantes de um ciclo."""
        context = get_request_context()
        return execute_tool(
            name="colaboradores_carga_trabalho",
            audit=audit,
            operation=lambda: service.carga_trabalho(context, id_ciclo, limit),
        )

    @mcp.tool(name="colaboradores_sugestao_realocacao", structured_output=True)
    def colaboradores_sugestao_realocacao(
        id_ciclo: int,
        area: str | None = None,
        cargo: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        """Sugere candidatos por menor carga e compatibilidade de área/cargo."""
        context = get_request_context()
        return execute_tool(
            name="colaboradores_sugestao_realocacao",
            audit=audit,
            operation=lambda: service.sugestao_realocacao(
                context,
                id_ciclo=id_ciclo,
                area=area,
                cargo=cargo,
                limit=limit,
            ),
        )

    @mcp.tool(name="colaboradores_relatorio_completo", structured_output=True)
    def colaboradores_relatorio_completo(
        id_ciclo: int,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Consolida participantes, carga e candidatos para realocação."""
        context = get_request_context()
        return execute_tool(
            name="colaboradores_relatorio_completo",
            audit=audit,
            operation=lambda: service.relatorio(context, id_ciclo, limit),
        )
