from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from psycopg_pool import ConnectionPool
from pymongo import MongoClient
from qdrant_client import QdrantClient

from acta_mcp.core.config import Settings
from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository
from acta_mcp.modules.common import AccessService

if TYPE_CHECKING:
    from acta_mcp.modules.ciclos.service import CiclosService
    from acta_mcp.modules.colaboradores.service import ColaboradoresService
    from acta_mcp.modules.faq.service import FaqService
    from acta_mcp.modules.formularios.service import FormulariosService
    from acta_mcp.modules.licoes.service import LicoesService
    from acta_mcp.modules.relatorios.service import RelatoriosService
    from acta_mcp.modules.tarefas.service import TarefasService
    from acta_mcp.modules.treinamentos.service import TreinamentosService


@dataclass(slots=True)
class Container:
    settings: Settings
    postgres_pool: ConnectionPool
    mongo_client: MongoClient
    qdrant_client: QdrantClient | None
    postgres: PostgresRepository
    mongo: MongoRepository
    access: AccessService
    ciclos: CiclosService
    tarefas: TarefasService
    colaboradores: ColaboradoresService
    formularios: FormulariosService
    relatorios: RelatoriosService
    treinamentos: TreinamentosService
    licoes: LicoesService
    faq: FaqService

    def close(self) -> None:
        self.postgres_pool.close()
        self.mongo_client.close()
        if self.qdrant_client is not None:
            self.qdrant_client.close()
