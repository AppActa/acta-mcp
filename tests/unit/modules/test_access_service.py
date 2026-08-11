from collections.abc import Sequence
from typing import Any

import pytest

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError
from acta_mcp.modules.common import AccessService


class FakePostgres:
    def __init__(self, rows: list[dict[str, Any] | None]) -> None:
        self.rows = rows

    def fetch_one(self, _query: str, _params: Sequence[Any] = ()) -> dict | None:
        return self.rows.pop(0)


def context(*permissions: str, usuario_id: int = 1, empresa_id: int = 1) -> RequestContext:
    return RequestContext(
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        permissoes=frozenset(permissions or ("read",)),
        trace_id="access-test",
    )


@pytest.mark.parametrize(
    ("tipo_usuario", "expected"),
    [("ADMIN", "admin"), ("GESTOR", "create"), ("COLABORADOR", "read")],
)
def test_resolve_request_context_uses_database_role(
    tipo_usuario: str,
    expected: str,
) -> None:
    access = AccessService(
        FakePostgres(
            [
                {
                    "id": 1,
                    "id_empresa": 1,
                    "tipo_usuario": tipo_usuario,
                    "status": "ATIVO",
                }
            ]
        )
    )

    resolved = access.resolve_request_context(context("admin"))

    assert resolved.permissoes == frozenset({expected})


def test_resolve_request_context_rejects_company_spoofing() -> None:
    access = AccessService(
        FakePostgres(
            [
                {
                    "id": 1,
                    "id_empresa": 2,
                    "tipo_usuario": "ADMIN",
                    "status": "ATIVO",
                }
            ]
        )
    )

    with pytest.raises(ValueError, match="empresa informada"):
        access.resolve_request_context(context("admin", empresa_id=1))


def test_non_admin_must_be_linked_to_cycle() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 10, "id_empresa": 1, "id_responsavel": 7, "papel_ciclo": None}]
        )
    )

    with pytest.raises(AuthorizationError, match="não está vinculado"):
        access.ensure_cycle(context("read"), 10)


def test_admin_can_access_company_cycle_without_membership() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 10, "id_empresa": 1, "id_responsavel": 7, "papel_ciclo": None}]
        )
    )

    cycle = access.ensure_cycle(context("admin"), 10)

    assert cycle["id"] == 10


def test_task_access_inherits_cycle_membership() -> None:
    access = AccessService(
        FakePostgres(
            [
                {"id_ciclo": 10, "id_empresa": 1},
                {"id": 10, "id_empresa": 1, "id_responsavel": 7, "papel_ciclo": None},
            ]
        )
    )

    with pytest.raises(AuthorizationError, match="não está vinculado"):
        access.ensure_task(context("read"), 99)
