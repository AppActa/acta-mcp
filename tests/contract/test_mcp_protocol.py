import socket
import threading
import time
from datetime import UTC, datetime

import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from acta_mcp.resources.catalogo_tools import TOOL_CATALOG
from acta_mcp.server import build_application

pytestmark = [pytest.mark.contract, pytest.mark.integration]

TOOL_ARGUMENTS = {
    "ciclo_visao_geral": {"id_ciclo": 1},
    "ciclo_problema_principal": {"id_ciclo": 1},
    "ciclo_causas_raiz": {"id_ciclo": 1},
    "ciclo_ishikawa": {"id_ciclo": 1},
    "ciclo_riscos_pendencias": {"id_ciclo": 1},
    "ciclo_treinamentos": {"id_ciclo": 1},
    "ciclo_participantes": {"id_ciclo": 1},
    "ciclo_relatorio_completo": {"id_ciclo": 1},
    "tarefas_consultar": {"id_ciclo": 1},
    "tarefas_atrasadas": {"id_ciclo": 1},
    "tarefas_concluidas": {"id_ciclo": 1},
    "tarefas_detalhes": {"id_tarefa": 1},
    "tarefas_por_responsavel": {"id_ciclo": 1},
    "tarefas_alertas_prazo": {"id_ciclo": 1},
    "tarefas_justificativas": {"id_ciclo": 1},
    "tarefas_relatorio_completo": {"id_ciclo": 1},
    "colaboradores_consultar": {},
    "colaborador_detalhes": {"id_colaborador": 2, "id_ciclo": 1},
    "colaboradores_participantes_ciclo": {"id_ciclo": 1},
    "colaboradores_por_area": {},
    "colaboradores_carga_trabalho": {"id_ciclo": 1},
    "colaboradores_competencias": {"id_ciclo": 1},
    "colaboradores_disponibilidade": {"id_ciclo": 1},
    "colaboradores_realocacoes": {"id_ciclo": 1},
    "colaboradores_sugestao_realocacao": {"id_ciclo": 1},
    "colaboradores_relatorio_completo": {"id_ciclo": 1},
    "formularios_listar": {"id_ciclo": 1},
    "formularios_detalhes": {"id_ciclo": 1, "id_formulario": "fenomeno-1"},
    "formularios_respostas": {"id_ciclo": 1},
    "formularios_resumo_respostas": {"id_ciclo": 1},
    "relatorios_listar": {"id_ciclo": 1},
    "relatorios_detalhes": {
        "id_ciclo": 1,
        "id_relatorio": "relatorio-executivo-1-v2",
    },
    "relatorios_mais_recente": {"id_ciclo": 1},
    "relatorios_contexto_ciclo": {"id_ciclo": 1},
    "predicoes_risco_atraso_tarefa": {"id_tarefa": 1},
    "predicoes_estimativa_conclusao_tarefa": {"id_tarefa": 1},
    "predicoes_risco_atraso_ciclo": {"id_ciclo": 1},
    "predicoes_estimativa_conclusao_ciclo": {"id_ciclo": 1},
    "predicoes_conclusao_treinamento": {"id_ciclo": 1, "id_treinamento": 1},
    "predicoes_sobrecarga_colaborador": {"id_ciclo": 1},
    "predicoes_atingimento_meta": {"id_ciclo": 1},
    "predicoes_respostas_atipicas": {"id_ciclo": 1, "id_formulario": "fenomeno-1"},
    "predicoes_tema_formulario": {"id_ciclo": 1, "id_formulario": "fenomeno-1"},
    "predicoes_recorrencia_problema": {"id_ciclo": 1},
    "memoria_garantir_sessao": {"session_id": "contract-session"},
    "memoria_salvar_mensagem": {
        "session_id": "contract-session",
        "role": "usuario",
        "content": "Prefiro respostas objetivas.",
        "agent": "pytest",
    },
    "memoria_obter_contexto": {
        "session_id": "contract-session",
        "pergunta": "Como devo responder?",
    },
    "memoria_material_resumo": {"session_id": "contract-session"},
    "memoria_atualizar_resumo": {
        "session_id": "contract-session",
        "resumo": "O usuário prefere respostas objetivas.",
        "resumido_ate": datetime.now(UTC).isoformat(),
    },
    "memoria_registrar": {
        "tipo": "preferencia",
        "conteudo": "Prefere respostas objetivas",
        "session_id_origem": "contract-session",
    },
    "memoria_buscar": {"pergunta": "Como o usuário prefere as respostas?"},
    "memoria_listar": {},
    "memoria_obter_consentimento": {},
    "memoria_configurar_consentimento": {"modo": "somente_explicitas"},
    "faq_retriever": {"question": "Como funciona o PDCA?"},
}


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def mcp_url(integration_settings):
    port = free_port()
    settings = integration_settings.model_copy(update={"port": port})
    _, app, _ = build_application(settings)
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=port,
            log_level="warning",
        )
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 15
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    if not server.started:
        raise RuntimeError("Servidor MCP de teste não iniciou.")
    try:
        yield f"http://127.0.0.1:{port}/mcp"
    finally:
        server.should_exit = True
        thread.join(timeout=10)


@pytest.mark.asyncio
async def test_list_tools_and_call_tool(mcp_url) -> None:
    headers = {
        "X-Acta-Usuario-Id": "1",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    async with streamablehttp_client(mcp_url, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listed = await session.list_tools()
            expected = {name for tools in TOOL_CATALOG.values() for name in tools}
            assert {tool.name for tool in listed.tools} == expected
            assert len(expected) == 56

            response = await session.call_tool(
                "tarefas_atrasadas",
                {"id_ciclo": 1, "limit": 10},
            )
            assert not response.isError
            assert response.structuredContent["status"] == "ok"
            assert response.structuredContent["count"] == 1


@pytest.mark.asyncio
async def test_every_registered_tool_executes_successfully(mcp_url) -> None:
    headers = {
        "X-Acta-Usuario-Id": "1",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    async with streamablehttp_client(mcp_url, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            for tool_name, arguments in TOOL_ARGUMENTS.items():
                response = await session.call_tool(tool_name, arguments)
                assert not response.isError, tool_name
                assert response.structuredContent is not None, tool_name
                assert response.structuredContent["status"] == "ok", tool_name

            listed_memories = await session.call_tool("memoria_listar", {})
            memories = listed_memories.structuredContent["memorias"]
            assert memories
            deleted = await session.call_tool("memoria_excluir", {"id_memoria": memories[0]["_id"]})
            assert deleted.structuredContent["status"] == "ok"
            assert deleted.structuredContent["excluida"] is True
