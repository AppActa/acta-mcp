from typing import Any

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.core.context import get_request_context
from acta_mcp.core.tooling import execute_tool


def register_ciclo_tools(mcp: FastMCP, container: Container) -> None:
    service = container.ciclos
    audit = container.audit

    def register(name: str, description: str, method):
        def handler(id_ciclo: int) -> dict[str, Any]:
            context = get_request_context()
            return execute_tool(
                name=name,
                audit=audit,
                operation=lambda: method(context, id_ciclo),
            )

        handler.__name__ = name
        handler.__doc__ = description
        mcp.tool(name=name, structured_output=True)(handler)

    register(
        "ciclo_visao_geral",
        "Consulta visão geral, contagens e status de um ciclo PDCA autorizado.",
        service.visao_geral,
    )
    register(
        "ciclo_problema_principal",
        "Consulta o problema principal e sua causa raiz prioritária.",
        service.problema_principal,
    )
    register(
        "ciclo_causas_raiz",
        "Lista causas raiz registradas para o ciclo.",
        service.causas_raiz,
    )

    @mcp.tool(name="ciclo_ishikawa", structured_output=True)
    def ciclo_ishikawa(id_ciclo: int, limit: int = 10) -> dict[str, Any]:
        """Consulta o diagrama de Ishikawa do ciclo no MongoDB."""
        context = get_request_context()
        return execute_tool(
            name="ciclo_ishikawa",
            audit=audit,
            operation=lambda: service.ishikawa(context, id_ciclo, limit),
        )

    register(
        "ciclo_riscos_pendencias",
        "Consolida tarefas, metas, planos e alertas em risco no ciclo.",
        service.riscos_pendencias,
    )
    register(
        "ciclo_treinamentos",
        "Lista treinamentos e participantes relacionados ao ciclo.",
        service.treinamentos,
    )
    register(
        "ciclo_participantes",
        "Lista os usuários participantes do ciclo e seus papéis.",
        service.participantes,
    )
    register(
        "ciclo_relatorio_completo",
        "Consolida a visão completa do ciclo em resultado estruturado.",
        service.relatorio,
    )
