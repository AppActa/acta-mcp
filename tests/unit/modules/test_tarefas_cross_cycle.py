import pytest

from acta_mcp.core.context import RequestContext
from acta_mcp.modules.tarefas.service import TarefasService


class Access:
    def authorized_cycle_ids(self, _context):
        return [3, 7]


class Repository:
    def __init__(self):
        self.calls = []

    def resumo_entre_ciclos(self, cycle_ids, company_id):
        self.calls.append(("summary", cycle_ids, company_id))
        return {"status": "ok", "por_ciclo": []}

    def consultar_entre_ciclos(self, cycle_ids, company_id, **filters):
        self.calls.append(("list", cycle_ids, company_id, filters))
        return [{"id": 1, "id_ciclo": 3}]


@pytest.fixture
def service():
    repository = Repository()
    context = RequestContext(usuario_id=5, empresa_id=11, permissoes=frozenset({"read"}), trace_id="t")
    return TarefasService(repository, Access()), repository, context


def test_cross_cycle_summary_uses_only_server_authorized_scope(service):
    tasks, repository, context = service

    assert tasks.resumo_entre_ciclos(context) == {"status": "ok", "por_ciclo": []}
    assert repository.calls == [("summary", [3, 7], 11)]


def test_cross_cycle_task_list_is_bounded_and_carries_cycle_ids(service):
    tasks, repository, context = service

    result = tasks.consultar_entre_ciclos(context, status="PENDENTE", limit=25)

    assert result == {"status": "ok", "count": 1, "tarefas": [{"id": 1, "id_ciclo": 3}]}
    assert repository.calls == [("list", [3, 7], 11, {
        "id_responsavel": None, "status": "PENDENTE", "prioridade": None, "limit": 25,
    })]


@pytest.mark.parametrize("limit", [0, 201])
def test_cross_cycle_task_list_rejects_out_of_range_limit(service, limit):
    tasks, repository, context = service

    with pytest.raises(ValueError, match="entre 1 e 200"):
        tasks.consultar_entre_ciclos(context, limit=limit)
    assert repository.calls == []
