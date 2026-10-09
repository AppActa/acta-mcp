from collections.abc import Sequence
from typing import Any

import pytest

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError
from acta_mcp.modules.common import AccessService


class FakePostgres:
    def __init__(
        self,
        rows: list[dict[str, Any] | None],
        cycle_rows: list[dict[str, Any]] | None = None,
    ) -> None:
        self.rows = rows
        self.cycle_rows = cycle_rows or []
        self.fetch_all_calls: list[tuple[str, Sequence[Any]]] = []

    def fetch_one(self, _query: str, _params: Sequence[Any] = ()) -> dict | None:
        return self.rows.pop(0)

    def fetch_all(self, query: str, params: Sequence[Any] = ()) -> list[dict]:
        self.fetch_all_calls.append((query, params))
        return self.cycle_rows


def context(
    *permissions: str,
    usuario_id: int = 1,
    empresa_id: int = 1,
    tipo_usuario: str | None = None,
) -> RequestContext:
    return RequestContext(
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        permissoes=frozenset(permissions or ("read",)),
        trace_id="access-test",
        tipo_usuario=tipo_usuario,
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
    assert getattr(resolved, "tipo_usuario", None) == tipo_usuario


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

    cycle = access.ensure_cycle(context("admin", tipo_usuario="ADMIN"), 10)

    assert cycle["id"] == 10


def test_cycle_write_requires_gestor_profile_and_membership() -> None:
    access = AccessService(
        FakePostgres(
            [
                {"id": 10, "id_empresa": 1, "id_responsavel": 1, "papel_ciclo": "OBSERVADOR"}
            ]
        )
    )

    with pytest.raises(AuthorizationError, match="Somente gestor"):
        access.ensure_cycle(context("create", tipo_usuario="COLABORADOR"), 10, operation="write")


def test_admin_cycle_write_is_denied_even_with_membership() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 10, "id_empresa": 1, "id_responsavel": 1, "papel_ciclo": "RESPONSAVEL"}]
        )
    )

    with pytest.raises(AuthorizationError, match="Somente gestor"):
        access.ensure_cycle(context("admin", tipo_usuario="ADMIN"), 10, operation="write")


def test_cycle_delete_is_always_denied() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 10, "id_empresa": 1, "id_responsavel": 1, "papel_ciclo": "RESPONSAVEL"}]
        )
    )

    with pytest.raises(AuthorizationError, match="Exclusão"):
        access.ensure_cycle(context("create", tipo_usuario="GESTOR"), 10, operation="delete")


def test_linked_gestor_can_write_cycle() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 10, "id_empresa": 1, "id_responsavel": 1, "papel_ciclo": "OBSERVADOR"}]
        )
    )

    cycle = access.ensure_cycle(context("create", tipo_usuario="GESTOR"), 10, operation="write")

    assert cycle["id"] == 10


def test_gestor_without_cycle_membership_cannot_write() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 10, "id_empresa": 1, "id_responsavel": 1, "papel_ciclo": None}]
        )
    )

    with pytest.raises(AuthorizationError, match="vinculado"):
        access.ensure_cycle(context("create", tipo_usuario="GESTOR"), 10, operation="write")


def test_cycle_from_another_company_is_denied_even_for_admin() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 10, "id_empresa": 2, "id_responsavel": 1, "papel_ciclo": None}]
        )
    )

    with pytest.raises(AuthorizationError, match="acesso a este ciclo"):
        access.ensure_cycle(context("admin", tipo_usuario="ADMIN"), 10)


def test_resolve_request_context_rejects_inactive_user() -> None:
    access = AccessService(
        FakePostgres(
            [{"id": 1, "id_empresa": 1, "tipo_usuario": "GESTOR", "status": "INATIVO"}]
        )
    )

    with pytest.raises(ValueError, match="não está ativo"):
        access.resolve_request_context(context("read"))


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
        access.ensure_task(context("read"), 99, 10)


def test_authorized_cycle_ids_are_limited_to_user_memberships() -> None:
    postgres = FakePostgres([], cycle_rows=[{"id": 10}, {"id": 12}])
    access = AccessService(postgres)

    cycle_ids = access.authorized_cycle_ids(context("read", usuario_id=7, empresa_id=3))

    assert cycle_ids == [10, 12]
    query, params = postgres.fetch_all_calls[0]
    assert "pdca.usuario_ciclo" in query
    assert params == (7, 3)


def test_admin_authorized_cycle_ids_include_only_company_cycles() -> None:
    postgres = FakePostgres([], cycle_rows=[{"id": 10}, {"id": 12}])
    access = AccessService(postgres)

    cycle_ids = access.authorized_cycle_ids(
        context("admin", usuario_id=7, empresa_id=3, tipo_usuario="ADMIN")
    )

    assert cycle_ids == [10, 12]
    query, params = postgres.fetch_all_calls[0]
    assert "pdca.usuario_ciclo" not in query
    assert "id_empresa = %s" in query
    assert params == (3,)
