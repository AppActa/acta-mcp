import pytest

from acta_mcp.core.config import Settings
from acta_mcp.core.security import constant_time_equals, parse_positive_int


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
