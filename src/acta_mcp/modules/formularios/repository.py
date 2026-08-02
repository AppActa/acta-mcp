from typing import Any

from bson import ObjectId

from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.serializers import serialize

FORM_ID_FIELDS = (
    "id_formulario",
    "formulario_id",
    "idFormulario",
    "formularioId",
    "id",
    "_id",
)
RESPONSE_FORM_ID_FIELDS = FORM_ID_FIELDS[:4]


def _identifier_variants(identifier: Any) -> list[Any]:
    variants: list[Any] = [identifier, str(identifier)]
    text = str(identifier)
    if text.isdigit():
        variants.append(int(text))
    if ObjectId.is_valid(text):
        variants.append(ObjectId(text))
    return list(dict.fromkeys(variants))


def _alias_filter(prefix: str, identifier: int) -> dict[str, Any]:
    snake = f"id_{prefix}"
    suffix = f"{prefix}_id"
    camel = prefix.title().replace("_", "")
    return {
        "$or": [
            {snake: {"$in": _identifier_variants(identifier)}},
            {suffix: {"$in": _identifier_variants(identifier)}},
            {f"id{camel}": {"$in": _identifier_variants(identifier)}},
            {f"{prefix.split('_')[0]}Id": {"$in": _identifier_variants(identifier)}},
        ]
    }


def _form_filter(identifier: str) -> dict[str, Any]:
    variants = _identifier_variants(identifier)
    return {"$or": [{field: {"$in": variants}} for field in FORM_ID_FIELDS]}


def _response_form_filter(identifier: str) -> dict[str, Any]:
    variants = _identifier_variants(identifier)
    return {"$or": [{field: {"$in": variants}} for field in RESPONSE_FORM_ID_FIELDS]}


def document_form_id(document: dict[str, Any]) -> str | None:
    for field in FORM_ID_FIELDS:
        value = document.get(field)
        if value is not None:
            return str(value)
    return None


def response_form_id(document: dict[str, Any]) -> str | None:
    for field in RESPONSE_FORM_ID_FIELDS:
        value = document.get(field)
        if value is not None:
            return str(value)
    return None


class FormulariosRepository:
    def __init__(self, mongo: MongoRepository) -> None:
        self.mongo = mongo
        self.database = mongo.database

    def listar_formularios(
        self,
        *,
        id_ciclo: int,
        empresa_id: int,
        limit: int,
    ) -> list[dict[str, Any]]:
        return self.mongo.find_by_ciclo(
            collection="formularios",
            id_ciclo=id_ciclo,
            empresa_id=empresa_id,
            limit=limit,
        )

    def obter_formulario(
        self,
        *,
        id_ciclo: int,
        empresa_id: int,
        id_formulario: str,
    ) -> dict[str, Any] | None:
        query = {
            "$and": [
                _alias_filter("ciclo", id_ciclo),
                _alias_filter("empresa", empresa_id),
                _form_filter(id_formulario),
            ]
        }
        document = self.database["formularios"].find_one(query)
        return serialize(document) if document is not None else None

    def listar_respostas(
        self,
        *,
        id_ciclo: int,
        empresa_id: int,
        formularios: list[dict[str, Any]],
        id_formulario: str | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        direct_scope = {
            "$and": [
                _alias_filter("ciclo", id_ciclo),
                _alias_filter("empresa", empresa_id),
            ]
        }
        authorized_ids = {
            identifier for form in formularios if (identifier := document_form_id(form)) is not None
        }
        if id_formulario is not None:
            authorized_ids = {id_formulario}

        scopes: list[dict[str, Any]] = [direct_scope]
        if authorized_ids:
            variants = [
                value for identifier in authorized_ids for value in _identifier_variants(identifier)
            ]
            scopes.append(
                {"$or": [{field: {"$in": variants}} for field in RESPONSE_FORM_ID_FIELDS]}
            )

        query: dict[str, Any] = {"$or": scopes}
        if id_formulario is not None:
            query = {"$and": [query, _response_form_filter(id_formulario)]}
        documents = list(
            self.database["respostas_formulario"]
            .find(query)
            .sort([("respondido_em", -1), ("criado_em", -1)])
            .limit(limit)
        )
        return serialize(documents)
