from collections.abc import Callable
from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_predicao_tools(mcp: FastMCP, container: Container) -> None:
    service = container.predicoes
    audit = container.audit

    def run(
        name: str,
        operation: Callable[[], dict[str, Any]],
        *,
        minimum_access: str = "read",
    ) -> dict[str, Any]:
        return execute_tool(
            name=name,
            audit=audit,
            operation=operation,
            minimum_access=minimum_access,
        )

    @mcp.tool(name="predicoes_risco_atraso_tarefa", structured_output=True)
    def risco_atraso_tarefa(id_tarefa: int) -> dict[str, Any]:
        """Estima a probabilidade de uma tarefa autorizada terminar atrasada."""
        context = get_request_context()
        return run(
            name="predicoes_risco_atraso_tarefa",
            operation=lambda: service.risco_atraso_tarefa(context, id_tarefa=id_tarefa),
        )

    @mcp.tool(name="predicoes_estimativa_conclusao_tarefa", structured_output=True)
    def estimativa_conclusao_tarefa(id_tarefa: int) -> dict[str, Any]:
        """Estima duração, data de conclusão e possível atraso de uma tarefa."""
        context = get_request_context()
        return run(
            name="predicoes_estimativa_conclusao_tarefa",
            operation=lambda: service.estimativa_conclusao_tarefa(context, id_tarefa=id_tarefa),
        )

    @mcp.tool(name="predicoes_risco_atraso_ciclo", structured_output=True)
    def risco_atraso_ciclo(id_ciclo: int) -> dict[str, Any]:
        """Estima a probabilidade de um ciclo autorizado terminar atrasado."""
        context = get_request_context()
        return run(
            name="predicoes_risco_atraso_ciclo",
            operation=lambda: service.risco_atraso_ciclo(context, id_ciclo=id_ciclo),
        )

    @mcp.tool(name="predicoes_estimativa_conclusao_ciclo", structured_output=True)
    def estimativa_conclusao_ciclo(id_ciclo: int) -> dict[str, Any]:
        """Estima duração, data de conclusão e possível atraso de um ciclo."""
        context = get_request_context()
        return run(
            name="predicoes_estimativa_conclusao_ciclo",
            operation=lambda: service.estimativa_conclusao_ciclo(context, id_ciclo=id_ciclo),
        )

    @mcp.tool(name="predicoes_conclusao_treinamento", structured_output=True)
    def conclusao_treinamento(id_ciclo: int, id_treinamento: int) -> dict[str, Any]:
        """Estima a chance de conclusão dos participantes de um treinamento."""
        context = get_request_context()
        return run(
            name="predicoes_conclusao_treinamento",
            operation=lambda: service.conclusao_treinamento(
                context, id_ciclo=id_ciclo, id_treinamento=id_treinamento
            ),
        )

    @mcp.tool(name="predicoes_sobrecarga_colaborador", structured_output=True)
    def sobrecarga_colaborador(
        id_ciclo: int,
        id_colaborador: int | None = None,
    ) -> dict[str, Any]:
        """Estima risco de sobrecarga para um ou todos os colaboradores do ciclo."""
        context = get_request_context()
        return run(
            name="predicoes_sobrecarga_colaborador",
            operation=lambda: service.sobrecarga_colaborador(
                context, id_ciclo=id_ciclo, id_colaborador=id_colaborador
            ),
        )

    @mcp.tool(name="predicoes_atingimento_meta", structured_output=True)
    def atingimento_meta(id_ciclo: int, id_meta: int | None = None) -> dict[str, Any]:
        """Estima a probabilidade de atingimento de uma ou mais metas do ciclo."""
        context = get_request_context()
        return run(
            name="predicoes_atingimento_meta",
            operation=lambda: service.atingimento_meta(context, id_ciclo=id_ciclo, id_meta=id_meta),
        )

    @mcp.tool(name="predicoes_respostas_atipicas", structured_output=True)
    def respostas_atipicas(
        id_ciclo: int,
        id_formulario: str,
        limit: int = 200,
    ) -> dict[str, Any]:
        """Detecta respostas de formulário estatisticamente atípicas."""
        context = get_request_context()
        return run(
            name="predicoes_respostas_atipicas",
            minimum_access="geral",
            operation=lambda: service.respostas_atipicas(
                context, id_ciclo=id_ciclo, id_formulario=id_formulario, limit=limit
            ),
        )

    @mcp.tool(name="predicoes_tema_formulario", structured_output=True)
    def tema_formulario(
        id_ciclo: int,
        id_formulario: str,
        limit: int = 200,
    ) -> dict[str, Any]:
        """Classifica temas das respostas usando o histórico rotulado da empresa."""
        context = get_request_context()
        return run(
            name="predicoes_tema_formulario",
            minimum_access="geral",
            operation=lambda: service.tema_formulario(
                context, id_ciclo=id_ciclo, id_formulario=id_formulario, limit=limit
            ),
        )

    @mcp.tool(name="predicoes_recorrencia_problema", structured_output=True)
    def recorrencia_problema(
        id_ciclo: int,
        id_problema: int | None = None,
    ) -> dict[str, Any]:
        """Estima recorrência de problemas usando problemas históricos rotulados."""
        context = get_request_context()
        return run(
            name="predicoes_recorrencia_problema",
            operation=lambda: service.recorrencia_problema(
                context, id_ciclo=id_ciclo, id_problema=id_problema
            ),
        )
