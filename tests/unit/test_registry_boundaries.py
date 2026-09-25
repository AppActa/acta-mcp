from acta_mcp.resources.catalogo_tools import TOOL_CATALOG


def test_mcp_catalog_contains_only_business_domain_tools():
    catalogued_tools = {name for tools in TOOL_CATALOG.values() for name in tools}

    assert not any(name.startswith("memoria_") for name in catalogued_tools)
    assert not any(name.startswith("skills_") for name in catalogued_tools)
    assert "faq_retriever" in catalogued_tools
