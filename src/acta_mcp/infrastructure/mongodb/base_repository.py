from typing import Any

from pymongo.database import Database

from acta_mcp.infrastructure.serializers import serialize


def _id_alias_filter(prefix: str, identifier: int) -> dict[str, Any]:
    snake = f"id_{prefix}"
    suffix = f"{prefix}_id"
    camel_prefix = f"id{prefix.title().replace('_', '')}"
    camel_suffix = f"{prefix.split('_')[0]}Id"
    return {
        "$or": [
            {snake: identifier},
            {snake: str(identifier)},
            {suffix: identifier},
            {suffix: str(identifier)},
            {camel_prefix: identifier},
            {camel_prefix: str(identifier)},
            {camel_suffix: identifier},
            {camel_suffix: str(identifier)},
        ]
    }


class MongoRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def find_by_ciclo(
        self,
        *,
        collection: str,
        id_ciclo: int,
        empresa_id: int,
        limit: int,
    ) -> list[dict]:
        query = {
            "$and": [
                _id_alias_filter("ciclo", id_ciclo),
                _id_alias_filter("empresa", empresa_id),
            ]
        }
        documents = list(self.database[collection].find(query).limit(limit))
        return serialize(documents)

    def ping(self) -> bool:
        return bool(self.database.client.admin.command("ping").get("ok"))
