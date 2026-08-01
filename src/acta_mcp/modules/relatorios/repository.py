from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.serializers import serialize

REPORT_ID_FIELDS = ("id_relatorio", "relatorio_id", "idRelatorio", "relatorioId", "_id")


def _identifier_variants(identifier: Any) -> list[Any]:
    variants: list[Any] = [identifier, str(identifier)]
    text = str(identifier)
    if text.isdigit():
        variants.append(int(text))
    if ObjectId.is_valid(text):
        variants.append(ObjectId(text))
    return list(dict.fromkeys(variants))


def _scope_alias(prefix: str, identifier: int) -> dict[str, Any]:
    title = prefix.title().replace("_", "")
    variants = _identifier_variants(identifier)
    return {
        "$or": [
            {f"id_{prefix}": {"$in": variants}},
            {f"{prefix}_id": {"$in": variants}},
            {f"id{title}": {"$in": variants}},
            {f"{prefix.split('_')[0]}Id": {"$in": variants}},
        ]
    }


def _report_filter(identifier: str) -> dict[str, Any]:
    variants = _identifier_variants(identifier)
    return {"$or": [{field: {"$in": variants}} for field in REPORT_ID_FIELDS]}


class RelatoriosRepository:
    def __init__(self, mongo: MongoRepository) -> None:
        self.collection = mongo.database["relatorios"]

    def ensure_indexes(self) -> None:
        self.collection.create_index(
            [("id_empresa", ASCENDING), ("id_ciclo", ASCENDING), ("atualizado_em", DESCENDING)],
            name="relatorios_por_empresa_ciclo_atualizacao",
        )
        self.collection.create_index(
            [("id_empresa", ASCENDING), ("id_relatorio", ASCENDING)],
            name="relatorio_id_por_empresa",
            unique=True,
            partialFilterExpression={"id_relatorio": {"$type": "string"}},
        )

    def listar(
        self,
        *,
        id_ciclo: int,
        empresa_id: int,
        tipo: str | None,
        formato: str | None,
        status: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        clauses: list[dict[str, Any]] = [
            _scope_alias("ciclo", id_ciclo),
            _scope_alias("empresa", empresa_id),
        ]
        for field, value in (("tipo", tipo), ("formato", formato), ("status", status)):
            if value is not None:
                clauses.append({field: value})
        documents = list(
            self.collection.find({"$and": clauses}, {"conteudo": 0})
            .sort([("atualizado_em", DESCENDING), ("criado_em", DESCENDING)])
            .limit(limit)
        )
        return serialize(documents)

    def obter(
        self,
        *,
        id_ciclo: int,
        empresa_id: int,
        id_relatorio: str,
    ) -> dict[str, Any] | None:
        document = self.collection.find_one(
            {
                "$and": [
                    _scope_alias("ciclo", id_ciclo),
                    _scope_alias("empresa", empresa_id),
                    _report_filter(id_relatorio),
                ]
            }
        )
        return serialize(document) if document is not None else None

    def mais_recente(
        self,
        *,
        id_ciclo: int,
        empresa_id: int,
        tipo: str | None,
    ) -> dict[str, Any] | None:
        clauses: list[dict[str, Any]] = [
            _scope_alias("ciclo", id_ciclo),
            _scope_alias("empresa", empresa_id),
        ]
        if tipo is not None:
            clauses.append({"tipo": tipo})
        document = self.collection.find_one(
            {"$and": clauses},
            sort=[("atualizado_em", DESCENDING), ("criado_em", DESCENDING)],
        )
        return serialize(document) if document is not None else None
