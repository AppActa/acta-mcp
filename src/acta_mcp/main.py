import argparse

import uvicorn

from acta_mcp.core.config import get_settings
from acta_mcp.core.context import build_context, reset_request_context, set_request_context
from acta_mcp.core.logging import configure_logging
from acta_mcp.server import build_application


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor MCP do ACTA")
    parser.add_argument(
        "--transport",
        choices=("http", "stdio"),
        default="http",
        help="Transporte MCP. HTTP é recomendado para produção.",
    )
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.acta_log_level)
    mcp, app, container = build_application(settings)

    if args.transport == "stdio":
        if settings.acta_auth_mode != "disabled":
            parser.error("stdio requer ACTA_AUTH_MODE=disabled.")
        container.postgres_pool.open(wait=True)
        container.mongo.ping()
        token = set_request_context(
            build_context(
                usuario_id=settings.acta_default_usuario_id,
                empresa_id=settings.acta_default_empresa_id,
            )
        )
        try:
            mcp.run(transport="stdio")
        finally:
            reset_request_context(token)
            container.close()
        return

    uvicorn.run(
        app,
        host=settings.acta_host,
        port=settings.port,
        log_level=settings.acta_log_level.lower(),
    )


if __name__ == "__main__":
    main()
