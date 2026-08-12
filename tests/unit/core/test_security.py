import pytest

from acta_mcp.core.config import Settings
from acta_mcp.core.context import RequestContext, build_context
from acta_mcp.core.exceptions import AuthorizationError
from acta_mcp.core.security import (
    constant_time_equals,
    current_access_level,
    parse_positive_int,
    require_access,
)


def test_api_key_is_required_in_production() -> None:
    with pytest.raises(ValueError):
        Settings(
            acta_env="production",
            acta_auth_mode="api_key",
            acta_mcp_api_key=None,
        )


def test_disabled_auth_is_rejected_in_production() -> None:
    with pytest.raises(ValueError):
        Settings(acta_env="production", acta_auth_mode="disabled")


def test_security_helpers() -> None:
    assert constant_time_equals("segredo", "segredo")
    assert not constant_time_equals("segredo", "outro")
    assert parse_positive_int("12", header="X-Test") == 12
    with pytest.raises(ValueError):
        parse_positive_int("0", header="X-Test")


def test_access_hierarchy_and_legacy_write_alias() -> None:
    def context(*permissions: str) -> RequestContext:
        return RequestContext(1, 1, frozenset(permissions), "access-test")

    assert current_access_level(context("read")) == "read"
    assert current_access_level(context("read", "write")) == "create"
    assert current_access_level(context("geral")) == "geral"
    assert current_access_level(context("admin")) == "admin"
    require_access(context("admin"), "geral")

    with pytest.raises(AuthorizationError):
        require_access(context("create"), "geral")

    with pytest.raises(ValueError, match="Nível de acesso inválido"):
        build_context(usuario_id=1, empresa_id=1, permissoes="superuser")
