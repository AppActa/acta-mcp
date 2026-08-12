from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from acta_mcp.core.config import Settings


def create_postgres_pool(settings: Settings) -> ConnectionPool:
    return ConnectionPool(
        conninfo=settings.database_url,
        min_size=settings.acta_postgres_pool_min_size,
        max_size=settings.acta_postgres_pool_max_size,
        timeout=settings.acta_postgres_timeout_seconds,
        kwargs={"row_factory": dict_row, "autocommit": True},
        open=False,
    )
