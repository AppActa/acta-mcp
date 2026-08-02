from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.modules.ciclos.tools import register_ciclo_tools
from acta_mcp.modules.colaboradores.tools import register_colaborador_tools
from acta_mcp.modules.formularios.tools import register_formulario_tools
from acta_mcp.modules.memoria.tools import register_memory_tools
from acta_mcp.modules.predicoes.tools import register_predicao_tools
from acta_mcp.modules.rag.tools import register_rag_tools
from acta_mcp.modules.relatorios.tools import register_relatorio_tools
from acta_mcp.modules.skills.tools import register_skill_tools
from acta_mcp.modules.tarefas.tools import register_tarefa_tools
from acta_mcp.prompts.registry import register_prompts
from acta_mcp.resources.registry import register_resources


def register_all(mcp: FastMCP, container: Container) -> None:
    register_ciclo_tools(mcp, container)
    register_tarefa_tools(mcp, container)
    register_colaborador_tools(mcp, container)
    register_formulario_tools(mcp, container)
    register_memory_tools(mcp, container)
    register_relatorio_tools(mcp, container)
    register_predicao_tools(mcp, container)
    register_rag_tools(mcp, container)
    register_skill_tools(mcp, container)
    register_resources(mcp, container)
    register_prompts(mcp)
