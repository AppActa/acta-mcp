from datetime import date, timedelta
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
    assert summary["total_formularios"] >= 1
    listed_forms = service.listar(context, id_ciclo=1)
    assert any(
        formulario["id_formulario"] == "fenomeno-1"
        for formulario in listed_forms["formularios"]
    )
    assert summary["total_respostas"] == 3
    assert any(
        pattern["campo"] == "Sintoma"
        and pattern["valor"] == "Retrabalho"
        and pattern["ocorrencias"] == 2
        for pattern in summary["padroes_repetidos"]
    )


def test_report_context_operation(container, context) -> None:
    service = container.relatorios
    context_result = service.contexto_ciclo(context, id_ciclo=1)
    assert_ok(context_result)
    assert context_result["somente_leitura"] is True
    assert "relatorios_existentes" not in context_result
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


def test_all_creation_operations(container, context) -> None:
    from acta_mcp.core.context import RequestContext

    admin = RequestContext(
        usuario_id=1,
        empresa_id=1,
        permissoes=frozenset({"admin"}),
        trace_id="creation-integration",
    )
    task = container.tarefas.criar(
        admin,
        id_ciclo=1,
        id_plano_acao=1,
        id_responsavel=2,
        titulo=f"Tarefa de integração {uuid4()}",
        descricao="Validar operações de criação",
        prioridade="MEDIA",
        data_fim_prevista=date.today() + timedelta(days=30),
    )["tarefa"]
    assert_ok(container.tarefas.atualizar(admin, id_tarefa=task["id"], prioridade="ALTA"))
    assert_ok(
        container.tarefas.atualizar_status(
            admin,
            id_tarefa=task["id"],
            status="EM_ANDAMENTO",
        )
    )
    form = container.formularios.criar_rascunho(
        admin,
        id_ciclo=1,
        titulo="Formulário de integração",
        tipo="TESTE",
    )["formulario"]
    assert_ok(
        container.formularios.adicionar_pergunta(
            admin,
            id_ciclo=1,
            id_formulario=form["id_formulario"],
            texto="O processo foi validado?",
            tipo_resposta="BOOLEANO",
        )
    )
    assert_ok(
        container.formularios.publicar(
            admin,
            id_ciclo=1,
            id_formulario=form["id_formulario"],
        )
    )

    assert_ok(
        container.ciclos.registrar_causa(
            admin,
            id_ciclo=1,
            id_problema=1,
            descricao="Falta de revisão sistemática",
        )
    )
    assert_ok(
        container.ciclos.adicionar_item_ishikawa(
            admin,
            id_ciclo=1,
            categoria="metodo",
            causa="Revisão sem periodicidade definida",
        )
    )

    assert_ok(
        container.treinamentos.criar(
            admin,
            id_ciclo=1,
            id_responsavel=1,
            titulo="Treinamento de integração",
            data_treinamento=date.today() + timedelta(days=15),
            participantes=[2],
        )
    )
