from collections.abc import Iterator

import pytest

from acta_mcp.core.config import Settings, env_str
from acta_mcp.core.context import RequestContext
from acta_mcp.server import create_container


@pytest.fixture(scope="session")
def integration_settings() -> Settings:
    qdrant_overrides = {}
    if api_key := env_str("TEST_QDRANT_API_KEY"):
        qdrant_overrides["qdrant_api_key"] = api_key
    if endpoint := env_str("TEST_QDRANT_CLUSTER_ENDPOINT"):
        qdrant_overrides["qdrant_cluster_endpoint"] = endpoint

    return Settings(
        acta_env="test",
        acta_auth_mode="disabled",
        database_url=env_str(
            "TEST_DATABASE_URL",
            "postgresql://acta:acta@localhost:5433/acta",
        ),
        mongodb_uri=env_str("TEST_MONGODB_URI", "mongodb://localhost:27018"),
        mongodb_database="acta",
        qdrant_collection_name=env_str(
            "TEST_QDRANT_COLLECTION_NAME",
            "acta_faq_test",
        ),
        **qdrant_overrides,
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
