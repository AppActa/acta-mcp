"""Garante que conteúdo publicado para modelos não revele armazenamento interno."""

import inspect
import json

from acta_mcp.resources.catalogo_tools import TOOL_CATALOG
from acta_mcp.resources.registry import register_resources

FORBIDDEN_DETAILS = (
    "postgresql",
    "mongodb",
    "qdrant",
    "collection",
    "banco de dados",
    "schema",
)


def test_catalog_does_not_expose_storage_details() -> None:
    published_content = json.dumps(TOOL_CATALOG, ensure_ascii=False).casefold()
    assert not any(detail in published_content for detail in FORBIDDEN_DETAILS)


def test_database_schema_resource_is_not_registered() -> None:
    source = inspect.getsource(register_resources)
    assert "acta://schema/database" not in source
    assert "acta://documentation" not in source
