from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.modules.ciclos.tools import register_ciclo_tools
from acta_mcp.modules.colaboradores.tools import register_colaborador_tools
from acta_mcp.modules.faq.tools import register_faq_tools
from acta_mcp.modules.formularios.tools import register_formulario_tools
from acta_mcp.modules.licoes.tools import register_licoes_tools
from acta_mcp.modules.predicoes.tools import register_predicao_tools
from acta_mcp.modules.relatorios.tools import register_relatorio_tools
from acta_mcp.modules.tarefas.tools import register_tarefa_tools
from acta_mcp.modules.treinamentos.tools import register_treinamento_tools
from acta_mcp.prompts.registry import register_prompts
from acta_mcp.resources.registry import register_resources


def register_all(mcp: FastMCP, container: Container) -> None:
    register_ciclo_tools(mcp, container)
    register_tarefa_tools(mcp, container)
    register_colaborador_tools(mcp, container)
    register_formulario_tools(mcp, container)
    register_relatorio_tools(mcp, container)
    register_predicao_tools(mcp, container)
    register_treinamento_tools(mcp, container)
    register_licoes_tools(mcp, container)
    register_faq_tools(mcp, container)
    register_resources(mcp, container)
    register_prompts(mcp)
