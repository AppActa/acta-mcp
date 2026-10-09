from collections.abc import Sequence
from typing import Any

import pytest

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.treinamentos.service import TreinamentosService


class FakePostgres:
    def __init__(self, user_companies: dict[int, int]) -> None:
        self.user_companies = user_companies

    def fetch_one(self, query: str, params: Sequence[Any] = ()) -> dict | None:
        if "FROM pdca.ciclo c" in query:
            return {
                "id": 9,
                "id_empresa": 4,
                "id_responsavel": 3,
                "papel_ciclo": "RESPONSAVEL" if params[0] == 3 else None,
            }
        if "FROM usuario_sistema" in query:
            user_id = params[0]
            return {
                "id": user_id,
                "id_empresa": self.user_companies.get(user_id, 4),
                "status": "ATIVO",
            }
        raise AssertionError(f"Consulta inesperada: {query}")


class FakeRepository:
    def __init__(self) -> None:
        self.created = []

    def criar(self, payload):
        self.created.append(payload)
        return {"id": 12}


def make_service(user_companies: dict[int, int] | None = None):
    repository = FakeRepository()
    access = AccessService(FakePostgres(user_companies or {}))
    service = TreinamentosService(repository, access)
    context = RequestContext(
        usuario_id=3,
        empresa_id=4,
        permissoes=frozenset({"create"}),
        trace_id="training-test",
        tipo_usuario="GESTOR",
    )
    return service, repository, context


def training_payload() -> dict:
    return {
        "id_ciclo": 9,
        "id_responsavel": 7,
        "titulo": "Treinamento",
        "data_treinamento": "2026-09-30",
        "participantes": [8],
    }


def test_create_training_accepts_same_company_users_without_cycle_links():
    service, repository, context = make_service()

    result = service.criar(context, **training_payload())

    assert result == {"status": "ok", "treinamento": {"id": 12}}
    assert len(repository.created) == 1


@pytest.mark.parametrize(
    "user_id",
    [7, 8],
    ids=["responsible", "participant"],
)
def test_create_training_rejects_users_from_another_company(user_id: int):
    service, repository, context = make_service({user_id: 5})

    with pytest.raises(AuthorizationError, match="não pertence à empresa autenticada"):
        service.criar(context, **training_payload())

    assert repository.created == []
