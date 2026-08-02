from collections.abc import Sequence
from typing import Any

from psycopg_pool import ConnectionPool

from acta_mcp.infrastructure.serializers import serialize


class PostgresRepository:
    def __init__(self, pool: ConnectionPool) -> None:
        self.pool = pool

    def fetch_all(self, query: str, params: Sequence[Any] = ()) -> list[dict]:
        with self.pool.connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return [serialize(dict(row)) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: Sequence[Any] = ()) -> dict | None:
        with self.pool.connection() as connection, connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            return serialize(dict(row)) if row else None

    def ping(self) -> bool:
        return self.fetch_one("SELECT TRUE AS ok;") == {"ok": True}
