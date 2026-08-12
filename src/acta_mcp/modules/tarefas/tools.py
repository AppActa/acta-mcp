from datetime import date
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_tarefa_tools(mcp: FastMCP, container: Container) -> None:
    service = container.tarefas
    audit = container.audit

    @mcp.tool(name="tarefas_consultar", structured_output=True)
    def tarefas_consultar(
        id_ciclo: int,
        id_responsavel: int | None = None,
        status: Literal[
            "PENDENTE",
            "EM_ANDAMENTO",
            "BLOQUEADA",
            "CONCLUIDA",
            "ATRASADA",
            "CANCELADA",
        ]
        | None = None,
        prioridade: Literal["BAIXA", "MEDIA", "ALTA", "CRITICA"] | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        apenas_atrasadas: bool = False,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Consulta tarefas autorizadas de um ciclo com filtros opcionais."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_consultar",
            audit=audit,
            operation=lambda: service.consultar(
                context,
                id_ciclo=id_ciclo,
                id_responsavel=id_responsavel,
                status=status,
                prioridade=prioridade,
                data_inicio=data_inicio,
                data_fim=data_fim,
                apenas_atrasadas=apenas_atrasadas,
                limit=limit,
            ),
        )

    @mcp.tool(name="tarefas_atrasadas", structured_output=True)
    def tarefas_atrasadas(id_ciclo: int, limit: int = 50) -> dict[str, Any]:
        """Lista tarefas atrasadas ou vencidas de um ciclo autorizado."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_atrasadas",
            audit=audit,
            operation=lambda: service.atrasadas(context, id_ciclo, limit),
        )

    @mcp.tool(name="tarefas_concluidas", structured_output=True)
    def tarefas_concluidas(
        id_ciclo: int,
        id_responsavel: int | None = None,
        prioridade: Literal["BAIXA", "MEDIA", "ALTA", "CRITICA"] | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        """Lista tarefas concluídas de um ciclo autorizado."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_concluidas",
            audit=audit,
            operation=lambda: service.concluidas(
                context,
                id_ciclo=id_ciclo,
                id_responsavel=id_responsavel,
                prioridade=prioridade,
                data_inicio=data_inicio,
                data_fim=data_fim,
                limit=limit,
            ),
        )

    @mcp.tool(name="tarefas_detalhes", structured_output=True)
    def tarefas_detalhes(id_tarefa: int) -> dict[str, Any]:
        """Consulta detalhes, dependências e bloqueios de uma tarefa autorizada."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_detalhes",
            audit=audit,
            operation=lambda: service.detalhes(context, id_tarefa),
        )

    @mcp.tool(name="tarefas_por_responsavel", structured_output=True)
    def tarefas_por_responsavel(
        id_ciclo: int,
        id_responsavel: int | None = None,
    ) -> dict[str, Any]:
        """Agrupa tarefas por responsável e status no ciclo."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_por_responsavel",
            audit=audit,
            operation=lambda: service.por_responsavel(
                context,
                id_ciclo,
                id_responsavel,
            ),
        )

    @mcp.tool(name="tarefas_alertas_prazo", structured_output=True)
    def tarefas_alertas_prazo(
        id_ciclo: int,
        somente_nao_lidos: bool = False,
    ) -> dict[str, Any]:
        """Consulta alertas de prazo das tarefas do ciclo."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_alertas_prazo",
            audit=audit,
            operation=lambda: service.alertas(context, id_ciclo, somente_nao_lidos),
        )

    @mcp.tool(name="tarefas_relatorio_completo", structured_output=True)
    def tarefas_relatorio_completo(id_ciclo: int, limit: int = 50) -> dict[str, Any]:
        """Consolida tarefas, atrasos, responsáveis e alertas de prazo."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_relatorio_completo",
            audit=audit,
            operation=lambda: service.relatorio(context, id_ciclo, limit),
        )

    @mcp.tool(name="tarefas_criar", structured_output=True)
    def tarefas_criar(
        id_ciclo: int,
        id_plano_acao: int,
        id_responsavel: int,
        titulo: str,
        descricao: str,
        data_fim_prevista: date,
        prioridade: Literal["BAIXA", "MEDIA", "ALTA", "CRITICA"] = "MEDIA",
    ) -> dict[str, Any]:
        """Cria uma tarefa pendente em um plano de ação autorizado."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_criar",
            audit=audit,
            minimum_access="create",
            operation=lambda: service.criar(
                context,
                id_ciclo=id_ciclo,
                id_plano_acao=id_plano_acao,
                id_responsavel=id_responsavel,
                titulo=titulo,
                descricao=descricao,
                prioridade=prioridade,
                data_fim_prevista=data_fim_prevista,
            ),
        )

    @mcp.tool(name="tarefas_atualizar", structured_output=True)
    def tarefas_atualizar(
        id_tarefa: int,
        titulo: str | None = None,
        descricao: str | None = None,
        id_responsavel: int | None = None,
        prioridade: Literal["BAIXA", "MEDIA", "ALTA", "CRITICA"] | None = None,
        data_fim_prevista: date | None = None,
    ) -> dict[str, Any]:
        """Atualiza campos permitidos de uma tarefa autorizada."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_atualizar",
            audit=audit,
            minimum_access="create",
            operation=lambda: service.atualizar(
                context,
                id_tarefa=id_tarefa,
                titulo=titulo,
                descricao=descricao,
                id_responsavel=id_responsavel,
                prioridade=prioridade,
                data_fim_prevista=data_fim_prevista,
            ),
        )

    @mcp.tool(name="tarefas_atualizar_status", structured_output=True)
    def tarefas_atualizar_status(
        id_tarefa: int,
        status: Literal[
            "PENDENTE",
            "EM_ANDAMENTO",
            "BLOQUEADA",
            "CONCLUIDA",
            "ATRASADA",
            "CANCELADA",
        ],
    ) -> dict[str, Any]:
        """Atualiza o status e as datas operacionais de uma tarefa."""
        context = get_request_context()
        return execute_tool(
            name="tarefas_atualizar_status",
            audit=audit,
            minimum_access="create",
            operation=lambda: service.atualizar_status(
                context,
                id_tarefa=id_tarefa,
                status=status,
            ),
        )
