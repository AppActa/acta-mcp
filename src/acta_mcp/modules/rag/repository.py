from hashlib import sha256
from typing import Any
from uuid import UUID, uuid5

from qdrant_client import QdrantClient, models

from acta_mcp.modules.rag.documents import ACTA_DOCS

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
    def __init__(
        self,
        client: QdrantClient,
        *,
        collection_name: str,
        embedding_model: str,
        vector_size: int,
    ) -> None:
        self.client = client
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.vector_size = vector_size

    def ensure_index(self) -> None:
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=self.vector_size,
                    distance=models.Distance.COSINE,
                ),
            )
        else:
            self._validate_collection()

        records = [self._record(document) for document in ACTA_DOCS]
        existing_points = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[record["id"] for record in records],
            with_payload=True,
            with_vectors=False,
        )
        existing_hashes = {
            str(point.id): (point.payload or {}).get("content_hash") for point in existing_points
        }
        changed = [
            record
            for record in records
            if existing_hashes.get(record["id"]) != record["payload"]["content_hash"]
        ]
        if not changed:
            return

        self.client.upsert(
            collection_name=self.collection_name,
            wait=True,
            points=[
                models.PointStruct(
                    id=record["id"],
                    vector=models.Document(
                        text=record["embedding_text"],
                        model=self.embedding_model,
                    ),
                    payload=record["payload"],
                )
                for record in changed
            ],
        )

    def search(self, question: str, limit: int) -> list[dict[str, Any]]:
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=models.Document(text=question, model=self.embedding_model),
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
        self.client.get_collections()
        return True

    def _validate_collection(self) -> None:
        info = self.client.get_collection(self.collection_name)
        vectors = info.config.params.vectors
        if not isinstance(vectors, models.VectorParams):
            raise ValueError(
                f"A collection Qdrant '{self.collection_name}' usa vetores nomeados; "
                "configure outra QDRANT_COLLECTION_NAME."
            )
        if vectors.size != self.vector_size or vectors.distance != models.Distance.COSINE:
            raise ValueError(
                f"A collection Qdrant '{self.collection_name}' não é compatível com "
                f"vetores cosine de dimensão {self.vector_size}."
            )

    def _record(self, document: dict[str, Any]) -> dict[str, Any]:
        document_id = str(document.get("id", "acta_doc"))
        embedding_text = format_document(document)
        content_hash = sha256(f"{self.embedding_model}\0{embedding_text}".encode()).hexdigest()
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
