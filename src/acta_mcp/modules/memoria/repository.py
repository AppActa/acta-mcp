from __future__ import annotations

import logging
import re
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from pymongo.database import Database
from qdrant_client import QdrantClient, models

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError, NotFoundError
from acta_mcp.infrastructure.serializers import serialize

logger = logging.getLogger(__name__)

PII_PATTERNS = (
    ("CPF", r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}"),
    ("CNPJ", r"\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}"),
    ("TELEFONE", r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}"),
    ("EMAIL", r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
)


def sanitize_text(text: str) -> str:
    sanitized = text.strip()
    for label, pattern in PII_PATTERNS:
        sanitized = re.sub(pattern, f"[{label} OMITIDO]", sanitized)
    return sanitized


class MemoryRepository:
    def __init__(
        self,
        database: Database,
        qdrant: QdrantClient,
        *,
        collection_name: str,
        embedding_model: str,
        vector_size: int,
        message_retention_days: int,
        inferred_retention_days: int,
    ) -> None:
        self.sessions = database["memoria_sessoes"]
        self.messages = database["memoria_mensagens"]
        self.memories = database["memoria_usuario"]
        self.consents = database["memoria_consentimentos"]
        self.qdrant = qdrant
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.vector_size = vector_size
        self.message_retention_days = message_retention_days
        self.inferred_retention_days = inferred_retention_days

    @staticmethod
    def _owner(context: RequestContext) -> dict[str, int]:
        return {"usuario_id": context.usuario_id, "empresa_id": context.empresa_id}

    def ensure_indexes(self) -> None:
        self.sessions.create_index("session_id", unique=True)
        self.sessions.create_index("expira_em", expireAfterSeconds=0)
        self.sessions.create_index([("empresa_id", 1), ("usuario_id", 1), ("atualizada_em", -1)])
        self.messages.create_index([("session_id", 1), ("criada_em", -1)])
        self.messages.create_index("expira_em", expireAfterSeconds=0)
        self.memories.create_index([("empresa_id", 1), ("usuario_id", 1), ("status", 1)])
        expiration_index = self.memories.index_information().get("expira_em_1")
        if expiration_index and "expireAfterSeconds" in expiration_index:
            self.memories.drop_index("expira_em_1")
        self.memories.create_index("expira_em")
        self.consents.create_index([("empresa_id", 1), ("usuario_id", 1)], unique=True)
        if not self.qdrant.collection_exists(self.collection_name):
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )
        else:
            info = self.qdrant.get_collection(self.collection_name)
            vectors = info.config.params.vectors
            if (
                not isinstance(vectors, models.VectorParams)
                or vectors.size != self.vector_size
                or vectors.distance != models.Distance.COSINE
            ):
                raise ValueError(
                    f"A collection Qdrant '{self.collection_name}' não é compatível "
                    f"com vetores cosine de dimensão {self.vector_size}."
                )
        for field_name, schema in (
            ("usuario_id", models.PayloadSchemaType.INTEGER),
            ("empresa_id", models.PayloadSchemaType.INTEGER),
            ("status", models.PayloadSchemaType.KEYWORD),
            ("tipo", models.PayloadSchemaType.KEYWORD),
        ):
            self.qdrant.create_payload_index(
                collection_name=self.collection_name,
                field_name=field_name,
                field_schema=schema,
                wait=True,
            )
        self.cleanup_expired()

    def cleanup_expired(self, context: RequestContext | None = None) -> int:
        query: dict[str, Any] = {
            "status": {"$in": ["ativa", "expirada_indice_pendente"]},
            "expira_em": {"$ne": None, "$lte": datetime.now(UTC)},
        }
        if context is not None:
            query.update(self._owner(context))
        ids = [item["_id"] for item in self.memories.find(query, {"_id": 1})]
        if not ids:
            return 0
        status = "expirada"
        try:
            self.qdrant.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=ids),
                wait=True,
            )
        except Exception:  # noqa: BLE001 - mantém bloqueado no Mongo e tenta depois
            status = "expirada_indice_pendente"
            logger.exception("Não foi possível remover vetores expirados do Qdrant.")
        self.memories.update_many(
            {"_id": {"$in": ids}},
            {"$set": {"status": status, "expirada_em": datetime.now(UTC)}},
        )
        return len(ids)

    def ensure_session(
        self,
        context: RequestContext,
        session_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        existing = self.sessions.find_one({"session_id": session_id})
        if existing and any(
            existing.get(key) != value for key, value in self._owner(context).items()
        ):
            raise AuthorizationError("A sessão não pertence ao usuário autenticado nesta empresa.")
        self.sessions.update_one(
            {"session_id": session_id, **self._owner(context)},
            {
                "$setOnInsert": {
                    "_id": str(uuid4()),
                    "session_id": session_id,
                    **self._owner(context),
                    "iniciada_em": now,
                    "resumo": "",
                    "resumido_ate": None,
                    "total_mensagens": 0,
                    "metadata": metadata or {},
                },
                "$set": {
                    "status": "aberta",
                    "atualizada_em": now,
                    "expira_em": now + timedelta(days=self.message_retention_days),
                },
            },
            upsert=True,
        )
        return serialize(self.sessions.find_one({"session_id": session_id, **self._owner(context)}))

    def add_message(
        self,
        context: RequestContext,
        *,
        session_id: str,
        role: str,
        content: str,
        agent: str | None,
        metadata: dict[str, Any],
    ) -> dict[str, Any]:
        self.ensure_session(context, session_id)
        now = datetime.now(UTC)
        document = {
            "_id": str(uuid4()),
            "session_id": session_id,
            **self._owner(context),
            "role": role,
            "content": sanitize_text(content)[:8000],
            "agent": agent,
            "metadata": metadata,
            "criada_em": now,
            "expira_em": now + timedelta(days=self.message_retention_days),
        }
        self.messages.insert_one(document)
        self.sessions.update_one(
            {"session_id": session_id, **self._owner(context)},
            {
                "$inc": {"total_mensagens": 1},
                "$set": {
                    "atualizada_em": now,
                    "expira_em": now + timedelta(days=self.message_retention_days),
                },
            },
        )
        return serialize(document)

    def session_context(
        self, context: RequestContext, session_id: str, limit: int
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        session = self.ensure_session(context, session_id)
        messages = list(
            self.messages.find({"session_id": session_id, **self._owner(context)})
            .sort("criada_em", -1)
            .limit(limit)
        )
        messages.reverse()
        return session, serialize(messages)

    def summary_material(
        self, context: RequestContext, session_id: str
    ) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        session = self.ensure_session(context, session_id)
        query: dict[str, Any] = {"session_id": session_id, **self._owner(context)}
        if session.get("resumido_ate"):
            query["criada_em"] = {"$gt": session["resumido_ate"]}
        messages = list(self.messages.find(query).sort("criada_em", 1))
        return session, serialize(messages)

    def update_summary(
        self,
        context: RequestContext,
        session_id: str,
        summary: str,
        summarized_until: datetime,
    ) -> None:
        result = self.sessions.update_one(
            {"session_id": session_id, **self._owner(context)},
            {
                "$set": {
                    "resumo": sanitize_text(summary)[:12000],
                    "resumido_ate": summarized_until,
                    "atualizada_em": datetime.now(UTC),
                }
            },
        )
        if result.matched_count == 0:
            raise NotFoundError("Sessão não encontrada.")

    def get_consent(self, context: RequestContext) -> dict[str, Any]:
        consent = self.consents.find_one(self._owner(context))
        if consent:
            return serialize(consent)
        return {**self._owner(context), "modo": "somente_explicitas", "retencao_dias": None}

    def set_consent(
        self, context: RequestContext, modo: str, retencao_dias: int | None
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        self.consents.update_one(
            self._owner(context),
            {
                "$set": {
                    **self._owner(context),
                    "modo": modo,
                    "retencao_dias": retencao_dias,
                    "atualizada_em": now,
                }
            },
            upsert=True,
        )
        if modo == "desativado":
            ids = [
                item["_id"]
                for item in self.memories.find(
                    {**self._owner(context), "status": "ativa"}, {"_id": 1}
                )
            ]
            self.memories.update_many(
                {**self._owner(context), "status": "ativa"},
                {"$set": {"status": "excluida", "excluida_em": now}},
            )
            self.messages.delete_many(self._owner(context))
            self.sessions.delete_many(self._owner(context))
            if ids:
                self.qdrant.delete(
                    self.collection_name, points_selector=models.PointIdsList(points=ids), wait=True
                )
        return self.get_consent(context)

    def store_memory(self, context: RequestContext, data: dict[str, Any]) -> dict[str, Any] | None:
        self.cleanup_expired(context)
        consent = self.get_consent(context)
        if consent["modo"] == "desativado":
            return None
        if data["origem"] == "inferida" and consent["modo"] != "automatica":
            return None
        now = datetime.now(UTC)
        retention = consent.get("retencao_dias")
        if retention is None and data["origem"] == "inferida":
            retention = self.inferred_retention_days
        memory_id = str(uuid4())
        document = {
            "_id": memory_id,
            **self._owner(context),
            **data,
            "conteudo": sanitize_text(data["conteudo"]),
            "status": "ativa",
            "criada_em": now,
            "atualizada_em": now,
            "expira_em": now + timedelta(days=retention) if retention else None,
        }
        duplicate = self.memories.find_one(
            {
                **self._owner(context),
                "status": "ativa",
                "tipo": document["tipo"],
                "conteudo": document["conteudo"],
            }
        )
        if duplicate:
            self._upsert_vector(context, duplicate)
            return serialize(duplicate)
        self.memories.insert_one(document)
        self._upsert_vector(context, document)
        return serialize(document)

    def _upsert_vector(self, context: RequestContext, document: dict[str, Any]) -> None:
        self.qdrant.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=[
                models.PointStruct(
                    id=document["_id"],
                    vector=models.Document(text=document["conteudo"], model=self.embedding_model),
                    payload={
                        "usuario_id": context.usuario_id,
                        "empresa_id": context.empresa_id,
                        "tipo": document["tipo"],
                        "status": "ativa",
                    },
                )
            ],
        )

    def list_memories(
        self, context: RequestContext, *, tipo: str | None, limit: int
    ) -> list[dict[str, Any]]:
        self.cleanup_expired(context)
        query: dict[str, Any] = {**self._owner(context), "status": "ativa"}
        if tipo:
            query["tipo"] = tipo
        return serialize(list(self.memories.find(query).sort("atualizada_em", -1).limit(limit)))

    def semantic_search(
        self, context: RequestContext, query: str, limit: int
    ) -> list[dict[str, Any]]:
        self.cleanup_expired(context)
        response = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=models.Document(text=query, model=self.embedding_model),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="usuario_id", match=models.MatchValue(value=context.usuario_id)
                    ),
                    models.FieldCondition(
                        key="empresa_id", match=models.MatchValue(value=context.empresa_id)
                    ),
                    models.FieldCondition(key="status", match=models.MatchValue(value="ativa")),
                ]
            ),
            with_payload=False,
            limit=limit,
        )
        scores = {str(point.id): float(point.score) for point in response.points}
        documents = {
            item["_id"]: item
            for item in self.memories.find(
                {"_id": {"$in": list(scores)}, **self._owner(context), "status": "ativa"}
            )
        }
        return [
            {**serialize(documents[memory_id]), "score": round(scores[memory_id], 6)}
            for memory_id in scores
            if memory_id in documents
        ]

    def delete_memory(self, context: RequestContext, memory_id: str) -> bool:
        result = self.memories.update_one(
            {"_id": memory_id, **self._owner(context), "status": "ativa"},
            {"$set": {"status": "excluida", "excluida_em": datetime.now(UTC)}},
        )
        if result.matched_count:
            self.qdrant.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(points=[memory_id]),
                wait=True,
            )
            return True
        return False
