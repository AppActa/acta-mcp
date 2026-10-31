import socket
import threading
import time

import pytest
import uvicorn
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from acta_mcp.resources.catalogo_tools import TOOL_CATALOG
from acta_mcp.server import build_application

pytestmark = [pytest.mark.contract, pytest.mark.integration]

TOOL_ARGUMENTS = {
    "tarefas_resumo_entre_ciclos": {},
    "tarefas_consultar_entre_ciclos": {"limit": 10},
    "licoes_listar_entre_ciclos": {"limit": 10},
    "ciclo_visao_geral": {"id_ciclo": 1},
    "ciclo_problema_principal": {"id_ciclo": 1},
    "ciclo_causas_raiz": {"id_ciclo": 1},
    "ciclo_ishikawa": {"id_ciclo": 1},
    "ciclo_riscos_pendencias": {"id_ciclo": 1},
    "ciclo_treinamentos": {"id_ciclo": 1},
    "ciclo_participantes": {"id_ciclo": 1},
    "ciclo_relatorio_completo": {"id_ciclo": 1},
    "ciclos_registrar_causa": {
        "id_ciclo": 1,
        "id_problema": 1,
        "descricao": "Causa registrada pelo teste de contrato",
    },
    "ciclos_adicionar_item_ishikawa": {
        "id_ciclo": 1,
        "categoria": "metodo",
        "causa": "Ausência de revisão periódica",
    },
    "tarefas_consultar": {"id_ciclo": 1},
    "tarefas_atrasadas": {"id_ciclo": 1},
    "tarefas_concluidas": {"id_ciclo": 1},
    "tarefas_detalhes": {"id_tarefa": 1, "id_ciclo": 1},
    "tarefas_por_responsavel": {"id_ciclo": 1},
    "tarefas_alertas_prazo": {"id_ciclo": 1},
    "tarefas_relatorio_completo": {"id_ciclo": 1},
    "tarefas_criar": {
        "id_ciclo": 1,
        "id_plano_acao": 1,
        "id_responsavel": 2,
        "titulo": "Tarefa criada pelo contrato",
        "descricao": "Validar as novas tools de escrita",
        "data_fim_prevista": "2026-12-31",
    },
    "tarefas_atualizar": {},
    "tarefas_atualizar_status": {},
    "colaboradores_consultar": {"id_ciclo": 1},
    "colaborador_detalhes": {"id_colaborador": 2, "id_ciclo": 1},
    "colaboradores_participantes_ciclo": {"id_ciclo": 1},
    "colaboradores_por_area": {},
    "colaboradores_carga_trabalho": {"id_ciclo": 1},
    "colaboradores_sugestao_realocacao": {"id_ciclo": 1},
    "colaboradores_relatorio_completo": {"id_ciclo": 1},
    "formularios_listar": {"id_ciclo": 1},
    "formularios_detalhes": {"id_ciclo": 1, "id_formulario": "fenomeno-1"},
    "formularios_respostas": {"id_ciclo": 1},
    "formularios_resumo_respostas": {"id_ciclo": 1},
    "formularios_criar_rascunho": {
        "id_ciclo": 1,
        "titulo": "Formulário do contrato",
        "tipo": "TESTE",
    },
    "formularios_adicionar_pergunta": {},
    "formularios_publicar": {},
    "relatorios_contexto_ciclo": {"id_ciclo": 1},
    "treinamentos_criar": {
        "id_ciclo": 1,
        "id_responsavel": 1,
        "titulo": "Treinamento do contrato",
        "data_treinamento": "2026-12-20",
        "participantes": [2],
    },
    "licoes_resumir": {"id_ciclo": 1},
    "licoes_perguntar": {"id_ciclo": 1, "pergunta": "O que aprendemos?"},
    "licoes_resumir_entre_ciclos": {"limit": 20},
    "licoes_perguntar_entre_ciclos": {"pergunta": "O que aprendemos?", "limit": 20},
    "faq_retriever": {"question": "Como funciona o PDCA?", "limit": 3},
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
        "X-Acta-Usuario-Id": "2",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "admin",
    }
    async with streamablehttp_client(mcp_url, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            listed = await session.list_tools()
            expected = {name for tools in TOOL_CATALOG.values() for name in tools}
            assert {tool.name for tool in listed.tools} == expected
            assert len(expected) == 46
            scoped_tools = {
                "ciclo_visao_geral",
                "ciclo_problema_principal",
                "ciclo_causas_raiz",
                "ciclo_ishikawa",
                "ciclo_riscos_pendencias",
                "ciclo_treinamentos",
                "ciclo_participantes",
                "ciclo_relatorio_completo",
                "ciclos_registrar_causa",
                "ciclos_adicionar_item_ishikawa",
                "tarefas_consultar",
                "tarefas_atrasadas",
                "tarefas_concluidas",
                "tarefas_detalhes",
                "tarefas_por_responsavel",
                "tarefas_alertas_prazo",
                "tarefas_relatorio_completo",
                "tarefas_criar",
                "tarefas_atualizar",
                "tarefas_atualizar_status",
                "colaboradores_consultar",
                "colaborador_detalhes",
                "colaboradores_participantes_ciclo",
                "colaboradores_carga_trabalho",
                "colaboradores_sugestao_realocacao",
                "colaboradores_relatorio_completo",
                "formularios_listar",
                "formularios_detalhes",
                "formularios_respostas",
                "formularios_resumo_respostas",
                "formularios_criar_rascunho",
                "formularios_adicionar_pergunta",
                "formularios_publicar",
                "relatorios_contexto_ciclo",
                "treinamentos_criar",
                "licoes_criar",
                "licoes_resumir",
                "licoes_perguntar",
            }
            for tool in listed.tools:
                if tool.name in scoped_tools:
                    assert "id_ciclo" in tool.inputSchema.get("required", []), tool.name

            response = await session.call_tool(
                "tarefas_atrasadas",
                {"id_ciclo": 1, "limit": 10},
            )
            assert not response.isError
            assert response.structuredContent["status"] == "ok"
            assert response.structuredContent["count"] >= 1
            assert any(
                tarefa["id"] == 1
                for tarefa in response.structuredContent["tarefas"]
            )


@pytest.mark.asyncio
async def test_every_registered_read_tool_executes_successfully(mcp_url) -> None:
    headers = {
        "X-Acta-Usuario-Id": "4",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    async with streamablehttp_client(mcp_url, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            mutating_tools = {
                "ciclos_registrar_causa",
                "ciclos_adicionar_item_ishikawa",
                "tarefas_criar",
                "tarefas_atualizar",
                "tarefas_atualizar_status",
                "formularios_criar_rascunho",
                "formularios_adicionar_pergunta",
                "formularios_publicar",
                "treinamentos_criar",
                "licoes_criar",
            }
            for tool_name, arguments in TOOL_ARGUMENTS.items():
                if tool_name in mutating_tools:
                    continue
                response = await session.call_tool(tool_name, arguments)
                assert not response.isError, tool_name
                assert response.structuredContent is not None, tool_name
                assert response.structuredContent["status"] in {"ok", "sem_licoes", "sem_evidencia"}, tool_name
                if tool_name == "faq_retriever":
                    assert response.structuredContent["count"] > 0



@pytest.mark.asyncio
async def test_cycle_read_access(mcp_url) -> None:
    async def call(headers, tool_name, arguments):
        async with streamablehttp_client(mcp_url, headers=headers) as streams:
            read_stream, write_stream, _ = streams
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments)

    read_headers = {
        "X-Acta-Usuario-Id": "2",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    allowed_form = await call(
        read_headers,
        "formularios_listar",
        {"id_ciclo": 1},
    )
    assert allowed_form.structuredContent["status"] == "ok"

    for tool_name, arguments in (
        ("relatorios_contexto_ciclo", {"id_ciclo": 1}),
    ):
        allowed_cycle_read = await call(
            read_headers,
            tool_name,
            arguments,
        )
        assert allowed_cycle_read.structuredContent["status"] != "forbidden"

    admin_headers = {
        "X-Acta-Usuario-Id": "4",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    allowed_admin_cycle = await call(
        admin_headers,
        "ciclo_visao_geral",
        {"id_ciclo": 1},
    )
    assert allowed_admin_cycle.structuredContent["status"] == "ok"

    unlinked_headers = {
        "X-Acta-Usuario-Id": "5",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "admin",
    }
    forbidden_cycle = await call(
        unlinked_headers,
        "ciclo_visao_geral",
        {"id_ciclo": 1},
    )
    assert forbidden_cycle.structuredContent["status"] == "forbidden"

