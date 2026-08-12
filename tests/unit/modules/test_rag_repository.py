from types import SimpleNamespace

from qdrant_client import models

from acta_mcp.modules.rag.documents import ACTA_DOCS
from acta_mcp.modules.rag.repository import FaqRepository


class FakeQdrantClient:
    def __init__(self) -> None:
        self.created: tuple[str, models.VectorParams] | None = None
        self.upserted: list[models.PointStruct] = []

    def collection_exists(self, collection_name: str) -> bool:
        return False

    def create_collection(
        self,
        *,
        collection_name: str,
        vectors_config: models.VectorParams,
    ) -> None:
        self.created = (collection_name, vectors_config)

    def retrieve(self, **_: object) -> list:
        return []

    def upsert(self, *, points: list[models.PointStruct], **_: object) -> None:
        self.upserted = points

    def query_points(self, **_: object) -> SimpleNamespace:
        return SimpleNamespace(
            points=[
                SimpleNamespace(
                    score=0.87654321,
                    payload={
                        "source": "ACTA_DOCS::intro_pdca",
                        "title": "Metodologia PDCA no ACTA",
                        "section": "Introdução",
                        "phase": None,
                        "content": "O ACTA organiza o processo com o ciclo PDCA.",
                    },
                )
            ]
        )


def test_ensure_index_creates_collection_and_upserts_documents() -> None:
    client = FakeQdrantClient()
    repository = FaqRepository(  # type: ignore[arg-type]
        client,
        collection_name="acta_faq_test",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        vector_size=384,
    )

    repository.ensure_index()

    assert client.created is not None
    assert client.created[0] == "acta_faq_test"
    assert client.created[1].size == 384
    assert client.created[1].distance == models.Distance.COSINE
    assert len(client.upserted) == len(ACTA_DOCS)
    assert all(point.payload["dataset"] == "ACTA_DOCS" for point in client.upserted)
    assert all(isinstance(point.vector, models.Document) for point in client.upserted)


def test_search_maps_qdrant_points_to_tool_contract() -> None:
    repository = FaqRepository(  # type: ignore[arg-type]
        FakeQdrantClient(),
        collection_name="acta_faq_test",
        embedding_model="sentence-transformers/all-MiniLM-L6-v2",
        vector_size=384,
    )

    results = repository.search("Como funciona o PDCA?", limit=3)

    assert results == [
        {
            "score": 0.876543,
            "source": "ACTA_DOCS::intro_pdca",
            "title": "Metodologia PDCA no ACTA",
            "section": "Introdução",
            "phase": None,
            "content": "O ACTA organiza o processo com o ciclo PDCA.",
        }
    ]
