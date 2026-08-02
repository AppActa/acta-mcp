from uuid import uuid4

import pytest

pytestmark = pytest.mark.integration


def assert_ok(result: dict) -> None:
    assert result["status"] == "ok", result


def test_all_cycle_operations(container, context) -> None:
    service = container.ciclos
    operations = [
        lambda: service.visao_geral(context, 1),
        lambda: service.problema_principal(context, 1),
        lambda: service.causas_raiz(context, 1),
        lambda: service.ishikawa(context, 1),
        lambda: service.riscos_pendencias(context, 1),
        lambda: service.treinamentos(context, 1),
        lambda: service.participantes(context, 1),
        lambda: service.relatorio(context, 1),
    ]
    for operation in operations:
        assert_ok(operation())


def test_all_task_operations(container, context) -> None:
    service = container.tarefas
    operations = [
        lambda: service.consultar(context, id_ciclo=1),
        lambda: service.atrasadas(context, 1),
        lambda: service.concluidas(context, id_ciclo=1),
        lambda: service.detalhes(context, 1),
        lambda: service.por_responsavel(context, 1),
        lambda: service.alertas(context, 1),
        lambda: service.justificativas(context, id_ciclo=1, id_tarefa=1),
        lambda: service.relatorio(context, 1),
    ]
    for operation in operations:
        assert_ok(operation())


def test_all_collaborator_operations(container, context) -> None:
    service = container.colaboradores
    operations = [
        lambda: service.consultar(context),
        lambda: service.detalhes(context, 2, 1),
        lambda: service.participantes(context, 1),
        lambda: service.por_area(context),
        lambda: service.carga_trabalho(context, 1),
        lambda: service.competencias(context, id_ciclo=1),
        lambda: service.disponibilidade(context, id_ciclo=1),
        lambda: service.realocacoes(context, id_ciclo=1),
        lambda: service.sugestao_realocacao(context, id_ciclo=1),
        lambda: service.relatorio(context, 1),
    ]
    for operation in operations:
        assert_ok(operation())


def test_all_form_operations(container, context) -> None:
    service = container.formularios
    operations = [
        lambda: service.listar(context, id_ciclo=1),
        lambda: service.detalhes(
            context,
            id_ciclo=1,
            id_formulario="fenomeno-1",
        ),
        lambda: service.respostas(context, id_ciclo=1),
        lambda: service.resumo_respostas(context, id_ciclo=1),
    ]
    for operation in operations:
        assert_ok(operation())

    summary = service.resumo_respostas(context, id_ciclo=1)
    assert summary["total_formularios"] == 1
    assert summary["total_respostas"] == 3
    assert any(
        pattern["campo"] == "Sintoma"
        and pattern["valor"] == "Retrabalho"
        and pattern["ocorrencias"] == 2
        for pattern in summary["padroes_repetidos"]
    )


def test_all_report_read_operations(container, context) -> None:
    service = container.relatorios
    service.ensure_indexes()
    operations = [
        lambda: service.listar(context, id_ciclo=1),
        lambda: service.detalhes(
            context,
            id_ciclo=1,
            id_relatorio="relatorio-executivo-1-v2",
        ),
        lambda: service.mais_recente(context, id_ciclo=1),
        lambda: service.contexto_ciclo(context, id_ciclo=1),
    ]
    for operation in operations:
        assert_ok(operation())

    listed = service.listar(context, id_ciclo=1)
    assert listed["count"] == 2
    assert all("conteudo" not in report for report in listed["relatorios"])
    latest = service.mais_recente(context, id_ciclo=1)
    assert latest["relatorio"]["id_relatorio"] == "relatorio-executivo-1-v2"
    context_result = service.contexto_ciclo(context, id_ciclo=1)
    assert context_result["somente_leitura"] is True
    assert "cpf" not in str(context_result).lower()


def test_all_prediction_operations(container, context) -> None:
    service = container.predicoes
    operations = [
        lambda: service.risco_atraso_tarefa(context, id_tarefa=1),
        lambda: service.estimativa_conclusao_tarefa(context, id_tarefa=1),
        lambda: service.risco_atraso_ciclo(context, id_ciclo=1),
        lambda: service.estimativa_conclusao_ciclo(context, id_ciclo=1),
        lambda: service.conclusao_treinamento(context, id_ciclo=1, id_treinamento=1),
        lambda: service.sobrecarga_colaborador(context, id_ciclo=1),
        lambda: service.atingimento_meta(context, id_ciclo=1),
        lambda: service.respostas_atipicas(context, id_ciclo=1, id_formulario="fenomeno-1"),
        lambda: service.tema_formulario(context, id_ciclo=1, id_formulario="fenomeno-1"),
        lambda: service.recorrencia_problema(context, id_ciclo=1),
    ]
    for operation in operations:
        result = operation()
        assert_ok(result)
        assert result["previsao_disponivel"] is False


def test_persistent_memory_lifecycle(container, context) -> None:
    service = container.memoria
    service.ensure_indexes()
    session_id = f"pytest-{uuid4()}"
    assert_ok(service.garantir_sessao(context, session_id=session_id))
    assert_ok(
        service.salvar_mensagem(
            context,
            session_id=session_id,
            role="usuario",
            content="Prefiro respostas curtas. email@example.com",
            agent="pytest",
            metadata={},
        )
    )
    stored = service.registrar(
        context,
        tipo="preferencia",
        conteudo=f"Prefere respostas curtas ({session_id})",
        origem="explicita",
        session_id_origem=session_id,
    )
    assert stored["salva"] is True
    memory_id = stored["memoria"]["_id"]

    result = service.obter_contexto(
        context,
        session_id=session_id,
        pergunta="Qual o formato de resposta preferido?",
    )
    assert_ok(result)
    assert "Prefere respostas curtas" in result["contexto"]
    assert "email@example.com" not in result["contexto"]
    assert "[EMAIL OMITIDO]" in result["contexto"]

    assert service.excluir(context, id_memoria=memory_id)["excluida"] is True


def test_memory_isolated_between_users(container, context) -> None:
    from acta_mcp.core.context import RequestContext
    from acta_mcp.core.exceptions import AuthorizationError

    service = container.memoria
    session_id = f"tenant-memory-{uuid4()}"
    other = RequestContext(
        usuario_id=2,
        empresa_id=context.empresa_id,
        permissoes=context.permissoes,
        trace_id="other-memory-user",
    )
    service.garantir_sessao(context, session_id=session_id)
    stored = service.registrar(
        context,
        tipo="objetivo",
        conteudo=f"Objetivo privado {session_id}",
        origem="explicita",
        session_id_origem=session_id,
    )

    with pytest.raises(AuthorizationError):
        service.garantir_sessao(other, session_id=session_id)
    assert service.buscar(other, pergunta=session_id)["memorias"] == []

    service.excluir(context, id_memoria=stored["memoria"]["_id"])


def test_personal_skill_lifecycle_and_user_isolation(container, context) -> None:
    from acta_mcp.core.context import RequestContext
    from acta_mcp.core.exceptions import NotFoundError

    write_context = RequestContext(
        usuario_id=context.usuario_id,
        empresa_id=context.empresa_id,
        permissoes=frozenset({"read", "write"}),
        trace_id="skill-owner",
    )
    other_user = RequestContext(
        usuario_id=2,
        empresa_id=context.empresa_id,
        permissoes=frozenset({"read", "write"}),
        trace_id="skill-other-user",
    )
    service = container.skills
    service.ensure_indexes()
    markdown = (
        "# Resumo Integração\n\n# objetivo\n\nResumir os resultados encontrados.\n\n"
        "# regras\n\n- Usar tópicos curtos.\n- Encerrar com próximos passos."
    )

    created = service.criar(write_context, conteudo_markdown=markdown)
    assert_ok(created)
    assert created["skill"]["comando"] == "/resumo-integracao"
    assert service.obter(write_context, nome="resumo-integracao")["status"] == "ok"
    with pytest.raises(NotFoundError):
        service.obter(other_user, nome="resumo-integracao")
    assert service.listar(other_user)["skills"] == []
    with pytest.raises(NotFoundError):
        service.excluir(other_user, nome="resumo-integracao")
    assert service.excluir(write_context, nome="resumo-integracao")["excluida"] is True


def test_tenant_isolation(container, context) -> None:
    from acta_mcp.core.exceptions import AuthorizationError

    with pytest.raises(AuthorizationError):
        container.ciclos.visao_geral(context, 2)
    with pytest.raises(AuthorizationError):
        container.tarefas.detalhes(context, 20)
    with pytest.raises(AuthorizationError):
        container.colaboradores.detalhes(context, 20)

    collaborators = container.colaboradores.consultar(context)
    assert {row["id_empresa"] for row in collaborators["colaboradores"]} == {1}

    forms = container.formularios.listar(context, id_ciclo=1)
    assert {row["id_empresa"] for row in forms["formularios"]} == {1}
    responses = container.formularios.respostas(context, id_ciclo=1)
    assert {row["id_empresa"] for row in responses["respostas"]} == {1}
    reports = container.relatorios.listar(context, id_ciclo=1)
    assert {row["id_empresa"] for row in reports["relatorios"]} == {1}
