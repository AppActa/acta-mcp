import json

from mcp.server.fastmcp import FastMCP

from acta_mcp.container import Container
from acta_mcp.resources.catalogo_tools import TOOL_CATALOG


def register_resources(mcp: FastMCP, container: Container) -> None:
    @mcp.resource("acta://catalog/tools")
    def tool_catalog() -> str:
        """Catálogo das tools por domínio."""
        return json.dumps(TOOL_CATALOG, ensure_ascii=False, indent=2)

    @mcp.resource("acta://documentation")
    def acta_documentation() -> str:
        """Documentação conceitual autorizada do ACTA."""
        return json.dumps(container.rag.documentation(), ensure_ascii=False)
