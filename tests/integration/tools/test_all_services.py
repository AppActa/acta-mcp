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
        lambda: service.conclusao_treinamento(
            context, id_ciclo=1, id_treinamento=1
        ),
        lambda: service.sobrecarga_colaborador(context, id_ciclo=1),
        lambda: service.atingimento_meta(context, id_ciclo=1),
        lambda: service.respostas_atipicas(
            context, id_ciclo=1, id_formulario="fenomeno-1"
        ),
        lambda: service.tema_formulario(
            context, id_ciclo=1, id_formulario="fenomeno-1"
        ),
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
    reports = container.relatorios.listar(context, id_ciclo=1)
    assert {row["id_empresa"] for row in reports["relatorios"]} == {1}
