from collections.abc import Iterator

import pytest

from acta_mcp.core.config import Settings, env_str
from acta_mcp.core.context import RequestContext
from acta_mcp.server import create_container


@pytest.fixture(scope="session")
def integration_settings() -> Settings:
    return Settings(
        acta_env="test",
        acta_auth_mode="disabled",
        database_url=env_str(
            "TEST_DATABASE_URL",
            "postgresql://acta:acta@localhost:5433/acta",
        ),
        mongodb_uri=env_str("TEST_MONGODB_URI", "mongodb://localhost:27018"),
        mongodb_database="acta",
    )


@pytest.fixture(scope="session")
def container(integration_settings) -> Iterator:
    instance = create_container(integration_settings)
    instance.postgres_pool.open(wait=True)
    instance.postgres.ping()
    instance.mongo.ping()
    try:
        yield instance
    finally:
        instance.close()


@pytest.fixture
def context() -> RequestContext:
    return RequestContext(
        usuario_id=1,
        empresa_id=1,
        permissoes=frozenset({"read"}),
        trace_id="pytest-trace",
    )
