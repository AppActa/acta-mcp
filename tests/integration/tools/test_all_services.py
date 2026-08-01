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
        lambda: service.perdas_ganhos(context, 1),
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

