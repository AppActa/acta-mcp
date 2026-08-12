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
    "tarefas_detalhes": {"id_tarefa": 1},
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
    "colaboradores_consultar": {},
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
    "memoria_garantir_sessao": {"session_id": "contract-session-admin"},
    "memoria_salvar_mensagem": {
        "session_id": "contract-session-admin",
        "role": "usuario",
        "content": "Prefiro respostas objetivas.",
        "agent": "pytest",
    },
    "memoria_obter_contexto": {
        "session_id": "contract-session-admin",
        "pergunta": "Como devo responder?",
    },
    "memoria_material_resumo": {"session_id": "contract-session-admin"},
    "memoria_atualizar_resumo": {
        "session_id": "contract-session-admin",
        "resumo": "O usuário prefere respostas objetivas.",
        "resumido_ate": datetime.now(UTC).isoformat(),
    },
    "memoria_registrar": {
        "tipo": "preferencia",
        "conteudo": "Prefere respostas objetivas",
        "session_id_origem": "contract-session-admin",
    },
    "memoria_buscar": {"pergunta": "Como o usuário prefere as respostas?"},
    "memoria_listar": {},
    "memoria_obter_consentimento": {},
    "memoria_configurar_consentimento": {"modo": "somente_explicitas"},
    "faq_retriever": {"question": "Como funciona o PDCA?"},
    "skills_criar": {
        "conteudo_markdown": (
            "# Resumo Contratual\n\n# objetivo\n\nResumir os resultados encontrados.\n\n"
            "# regras\n\n- Usar tópicos curtos.\n- Encerrar com próximos passos."
        )
    },
    "skills_obter": {"nome": "resumo-contratual"},
    "skills_listar": {},
    "skills_excluir": {"nome": "resumo-contratual"},
    "licoes_aprendidas_registrar": {
        "id_ciclo": 1,
        "titulo": "Lição do contrato",
        "licao": "Validar mutações com isolamento por empresa.",
    },
    "treinamentos_criar": {
        "id_ciclo": 1,
        "id_responsavel": 1,
        "titulo": "Treinamento do contrato",
        "data_treinamento": "2026-12-20",
        "participantes": [2],
    },
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
            assert len(expected) == 63

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
async def test_every_registered_tool_executes_successfully(mcp_url) -> None:
    headers = {
        "X-Acta-Usuario-Id": "4",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    async with streamablehttp_client(mcp_url, headers=headers) as streams:
        read_stream, write_stream, _ = streams
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            created_form_id = None
            created_task_id = None
            for tool_name, arguments in TOOL_ARGUMENTS.items():
                if tool_name == "tarefas_atualizar":
                    arguments = {"id_tarefa": created_task_id, "prioridade": "ALTA"}
                elif tool_name == "tarefas_atualizar_status":
                    arguments = {"id_tarefa": created_task_id, "status": "EM_ANDAMENTO"}
                elif tool_name == "formularios_adicionar_pergunta":
                    arguments = {
                        "id_ciclo": 1,
                        "id_formulario": created_form_id,
                        "texto": "A validação foi concluída?",
                        "tipo_resposta": "BOOLEANO",
                    }
                elif tool_name == "formularios_publicar":
                    arguments = {"id_ciclo": 1, "id_formulario": created_form_id}
                response = await session.call_tool(tool_name, arguments)
                assert not response.isError, tool_name
                assert response.structuredContent is not None, tool_name
                assert response.structuredContent["status"] == "ok", tool_name
                if tool_name == "tarefas_criar":
                    created_task_id = response.structuredContent["tarefa"]["id"]
                elif tool_name == "formularios_criar_rascunho":
                    created_form_id = response.structuredContent["formulario"]["id_formulario"]

            listed_memories = await session.call_tool("memoria_listar", {})
            memories = listed_memories.structuredContent["memorias"]
            assert memories
            deleted = await session.call_tool("memoria_excluir", {"id_memoria": memories[0]["_id"]})
            assert deleted.structuredContent["status"] == "ok"
            assert deleted.structuredContent["excluida"] is True


@pytest.mark.asyncio
async def test_access_levels(mcp_url) -> None:
    async def call(headers, tool_name, arguments):
        async with streamablehttp_client(mcp_url, headers=headers) as streams:
            read_stream, write_stream, _ = streams
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                return await session.call_tool(tool_name, arguments)

    read_headers = {
        "X-Acta-Usuario-Id": "2",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "admin",
    }
    forbidden_create = await call(
        read_headers,
        "tarefas_criar",
        {
            "id_ciclo": 1,
            "id_plano_acao": 1,
            "id_responsavel": 2,
            "titulo": "Não deve criar",
            "descricao": "Nível read não pode criar tarefas",
            "data_fim_prevista": "2026-12-31",
        },
    )
    assert forbidden_create.structuredContent["status"] == "forbidden"

    create_headers = {
        "X-Acta-Usuario-Id": "1",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    forbidden_form = await call(
        create_headers,
        "formularios_listar",
        {"id_ciclo": 1},
    )
    assert forbidden_form.structuredContent["status"] == "forbidden"

    for tool_name, arguments in (
        ("relatorios_contexto_ciclo", {"id_ciclo": 1}),
        (
            "predicoes_respostas_atipicas",
            {"id_ciclo": 1, "id_formulario": "fenomeno-1"},
        ),
        (
            "predicoes_tema_formulario",
            {"id_ciclo": 1, "id_formulario": "fenomeno-1"},
        ),
    ):
        forbidden_indirect_form_access = await call(
            create_headers,
            tool_name,
            arguments,
        )
        assert forbidden_indirect_form_access.structuredContent["status"] == "forbidden"

    geral_headers = {
        "X-Acta-Usuario-Id": "4",
        "X-Acta-Empresa-Id": "1",
        "X-Acta-Permissoes": "read",
    }
    allowed_form = await call(
        geral_headers,
        "formularios_listar",
        {"id_ciclo": 1},
    )
    assert allowed_form.structuredContent["status"] == "ok"

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

    skill_name = "Skill Read Access"
    skill_created = await call(
        read_headers,
        "skills_criar",
        {
            "conteudo_markdown": (
                f"# {skill_name}\n\n# objetivo\n\nResumir resultados.\n\n# regras\n"
            )
        },
    )
    assert skill_created.structuredContent["status"] == "ok"
    command = skill_created.structuredContent["skill"]["comando"]
    skill_deleted = await call(read_headers, "skills_excluir", {"nome": command})
    assert skill_deleted.structuredContent["status"] == "ok"
