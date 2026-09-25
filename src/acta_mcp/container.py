from dataclasses import dataclass

from psycopg_pool import ConnectionPool
from pymongo import MongoClient

from acta_mcp.core.config import Settings
from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.observability.audit import AuditLogger
from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository
from acta_mcp.modules.common import AccessService


@dataclass(slots=True)
class Container:
    settings: Settings
    postgres_pool: ConnectionPool
    mongo_client: MongoClient
    qdrant_client: object | None
    postgres: PostgresRepository
    mongo: MongoRepository
    access: AccessService
    audit: AuditLogger
    ciclos: object | None = None
    tarefas: object | None = None
    colaboradores: object | None = None
    formularios: object | None = None
    relatorios: object | None = None
    predicoes: object | None = None
    treinamentos: object | None = None
    licoes: object | None = None
    faq: object | None = None

    def close(self) -> None:
        self.postgres_pool.close()
        self.mongo_client.close()
        if self.qdrant_client is not None:
            self.qdrant_client.close()
