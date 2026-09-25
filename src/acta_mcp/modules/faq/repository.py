import re
import unicodedata
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid5

from qdrant_client import QdrantClient, models

from acta_mcp.core.config import Settings
from acta_mcp.modules.faq.documents import ACTA_DOCS
from acta_mcp.modules.faq.embeddings import MODEL, VECTOR_SIZE, embed_documents, embed_query

FAQ_NAMESPACE = UUID("c77e3733-c428-4f4f-89aa-9e5f5a750594")
DATASET_NAME = "ACTA_DOCS"


def format_document(document: dict[str, Any]) -> str:
    questions = "\n".join(f"- {question}" for question in document.get("example_questions", []))
    return (
        f"# {document.get('title', '')}\n\n"
        f"Seção: {document.get('section', '')}\n"
        f"Fase PDCA: {document.get('phase') or 'N/A'}\n"
        f"Público: {', '.join(document.get('audience', []))}\n"
        f"Tags: {', '.join(document.get('tags', []))}\n\n"
        f"{document.get('content', '')}\n\n"
        f"Perguntas relacionadas:\n{questions}"
    )


class FaqRepository:
    def __init__(self, client: QdrantClient | None, settings: Settings) -> None:
        self.client = client
        self.settings = settings

    def ensure_index(self) -> None:
        if self.client is None:
            return
        collection = self.settings.qdrant_faq_collection
        if not self.client.collection_exists(collection):
            self.client.create_collection(
                collection_name=collection,
                vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
            )
        else:
            self._validate_collection()

        records = [self._record(document) for document in ACTA_DOCS]
        existing = self.client.retrieve(
            collection_name=collection,
            ids=[record["id"] for record in records],
            with_payload=True,
            with_vectors=False,
        )
        hashes = {
            str(point.id): (point.payload or {}).get("content_hash") for point in existing
        }
        changed = [
            record
            for record in records
            if hashes.get(record["id"]) != record["payload"]["content_hash"]
        ]
        if changed:
            vectors = embed_documents(self.settings, [record["embedding_text"] for record in changed])
            self.client.upsert(
                collection_name=collection,
                wait=True,
                points=[
                    models.PointStruct(id=record["id"], vector=vector, payload=record["payload"])
                    for record, vector in zip(changed, vectors, strict=True)
                ],
            )

    def search(self, question: str, limit: int) -> list[dict[str, Any]]:
        if self.client is None:
            return self._lexical_search(question, limit)
        response = self.client.query_points(
            collection_name=self.settings.qdrant_faq_collection,
            query=embed_query(self.settings, question),
            with_payload=True,
            limit=limit,
        )
        results = []
        for point in response.points:
            payload = point.payload or {}
            results.append(
                {
                    "score": round(float(point.score), 6),
                    "source": payload.get("source", DATASET_NAME),
                    "title": payload.get("title", ""),
                    "section": payload.get("section", ""),
                    "phase": payload.get("phase"),
                    "content": payload.get("content", ""),
                }
            )
        return results

    def ping(self) -> bool:
        if self.client is not None:
            self.client.get_collections()
        return True

    @staticmethod
    def _lexical_search(question: str, limit: int) -> list[dict[str, Any]]:
        def terms(value: str) -> set[str]:
            plain = "".join(
                char
                for char in unicodedata.normalize("NFKD", value.casefold())
                if not unicodedata.combining(char)
            )
            return set(re.findall(r"[a-z0-9]+", plain)) - {
                "como", "para", "qual", "que", "uma", "com"
            }

        query = terms(question)
        ranked = []
        for document in ACTA_DOCS:
            searchable = " ".join(
                [
                    document.get("title", ""),
                    document.get("section", ""),
                    document.get("content", ""),
                    " ".join(document.get("tags", [])),
                    " ".join(document.get("example_questions", [])),
                ]
            )
            overlap = query & terms(searchable)
            if overlap:
                ranked.append((len(overlap) / max(len(query), 1), document))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [
            {
                "score": round(score, 6),
                "source": f"{DATASET_NAME}::{document['id']}",
                "title": document.get("title", ""),
                "section": document.get("section", ""),
                "phase": document.get("phase"),
                "content": format_document(document),
            }
            for score, document in ranked[:limit]
        ]

    def _validate_collection(self) -> None:
        info = self.client.get_collection(self.settings.qdrant_faq_collection)
        vectors = info.config.params.vectors
        if not isinstance(vectors, models.VectorParams):
            raise ValueError("A coleção Qdrant FAQ usa vetores nomeados e não é compatível.")
        if vectors.size != VECTOR_SIZE or vectors.distance != models.Distance.COSINE:
            raise ValueError(
                f"A coleção Qdrant FAQ deve usar vetores cosine de dimensão {VECTOR_SIZE}."
            )

    @staticmethod
    def _record(document: dict[str, Any]) -> dict[str, Any]:
        document_id = str(document.get("id", "acta_doc"))
        embedding_text = format_document(document)
        content_hash = sha256(f"{MODEL}\0{embedding_text}".encode()).hexdigest()
        return {
            "id": str(uuid5(FAQ_NAMESPACE, document_id)),
            "embedding_text": embedding_text,
            "payload": {
                "dataset": DATASET_NAME,
                "document_id": document_id,
                "content_hash": content_hash,
                "source": f"{DATASET_NAME}::{document_id}",
                "title": document.get("title", ""),
                "section": document.get("section", ""),
                "phase": document.get("phase"),
                "audience": document.get("audience", []),
                "tags": document.get("tags", []),
                "related_agents": document.get("related_agents", []),
                "content": embedding_text,
            },
        }
