import inspect

from acta_mcp.core.context import RequestContext
from acta_mcp.modules.colaboradores.schemas import ColaboradoresQuery
from acta_mcp.modules.colaboradores.service import ColaboradoresService


class Access:
    def __init__(self):
        self.cycles = []

    def ensure_cycle(self, context, id_ciclo):
        self.cycles.append((context.empresa_id, id_ciclo))

    def ensure_collaborator(self, _context, _id_colaborador):
        pass


class Repository:
    def consultar(self, payload, _empresa_id):
        return [{"id_ciclo": payload.id_ciclo}]

    def detalhes(self, _id_colaborador, _empresa_id, _id_ciclo):
        return {"id_usuario": 5}

    def ciclos(self, _id_usuario, _empresa_id, id_ciclo):
        return [{"id_ciclo": id_ciclo}]

    def tarefas(self, _id_usuario, _empresa_id, id_ciclo):
        return [{"id_ciclo": id_ciclo}]


def make_service():
    access = Access()
    service = ColaboradoresService(Repository(), access)
    context = RequestContext(
        usuario_id=3,
        empresa_id=4,
        permissoes=frozenset({"read"}),
        trace_id="collaborators-test",
    )
    return service, access, context


def test_cycle_scoped_collaborator_query_requires_cycle_in_schema():
    assert ColaboradoresQuery.model_fields["id_ciclo"].is_required()


def test_collaborator_query_validates_cycle_before_repository_read():
    service, access, context = make_service()

    result = service.consultar(context, id_ciclo=9)

    assert access.cycles == [(4, 9)]
    assert result["colaboradores"] == [{"id_ciclo": 9}]


def test_collaborator_details_only_returns_authorized_cycle():
    service, access, context = make_service()

    result = service.detalhes(context, 14, id_ciclo=9)

    assert access.cycles == [(4, 9)]
    assert result["ciclos"] == [{"id_ciclo": 9}]
    assert result["tarefas"] == [{"id_ciclo": 9}]


def test_collaborator_details_requires_cycle_argument():
    parameter = inspect.signature(ColaboradoresService.detalhes).parameters["id_ciclo"]

    assert parameter.default is inspect.Parameter.empty
