from typing import Any

from pymongo import ASCENDING, DESCENDING

from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.serializers import serialize


class LicoesAprendidasRepository:
    def __init__(self, mongo: MongoRepository) -> None:
        self.collection = mongo.database["licoes_aprendidas"]

    def ensure_indexes(self) -> None:
        self.collection.create_index(
            [("id_empresa", ASCENDING), ("id_ciclo", ASCENDING), ("criado_em", DESCENDING)],
            name="licoes_por_empresa_ciclo",
        )

    def criar(self, document: dict[str, Any]) -> dict[str, Any]:
        self.collection.insert_one(document)
        return serialize(document)

