from types import SimpleNamespace

import pytest

from acta_mcp.core.config import Settings
from acta_mcp.modules.faq import repository as faq_repository
from acta_mcp.modules.faq.repository import FaqRepository
from acta_mcp.modules.faq.service import FaqService


class Repository:
    def __init__(self):
        self.indexed = 0
        self.queries = []

    def ensure_index(self):
        self.indexed += 1

    def search(self, question, limit):
        self.queries.append((question, limit))
        return [{"title": "PDCA", "content": "Planejar, fazer, checar e agir."}]

    def ping(self):
        return True


def test_faq_search_returns_document_results_and_initializes_once():
    repository = Repository()
    service = FaqService(repository)

    first = service.search(" Como funciona o PDCA? ", 3)
    second = service.search("PDCA", 1)

    assert first == {
        "status": "ok",
        "count": 1,
        "resultados": [{"title": "PDCA", "content": "Planejar, fazer, checar e agir."}],
    }
    assert second["count"] == 1
    assert repository.indexed == 1
    assert repository.queries == [("Como funciona o PDCA?", 3), ("PDCA", 1)]


def test_faq_repository_uses_lexical_fallback_without_qdrant():
    settings = Settings(acta_env="test", acta_auth_mode="disabled")
    repository = FaqRepository(None, settings)

    results = repository.search("Como funciona o ciclo PDCA?", 3)

    assert results
    assert any("PDCA" in item["content"] for item in results)


def test_faq_repository_uses_qdrant_vectors_when_configured(monkeypatch):
    class Qdrant:
        def __init__(self):
            self.points = []
            self.query = None

        def collection_exists(self, _collection):
            return False

        def create_collection(self, **_kwargs):
            pass

        def retrieve(self, **_kwargs):
            return []

        def upsert(self, **kwargs):
            self.points = kwargs["points"]

        def query_points(self, **kwargs):
            self.query = kwargs
            return SimpleNamespace(
                points=[
                    SimpleNamespace(
                        score=0.9,
                        payload={"title": "PDCA", "content": "Documento vetorial", "source": "pdca"},
                    )
                ]
            )

    monkeypatch.setattr(
        faq_repository,
        "embed_documents",
        lambda _settings, texts: [[0.1] * 768 for _ in texts],
    )
    monkeypatch.setattr(faq_repository, "embed_query", lambda *_args: [0.1] * 768)
    client = Qdrant()
    settings = Settings(
        acta_env="test", acta_auth_mode="disabled", gemini_api_key="test-key"
    )
    repository = FaqRepository(client, settings)

    repository.ensure_index()
    result = repository.search("PDCA", 2)

    assert client.points
    assert client.query["collection_name"] == settings.qdrant_faq_collection
    assert client.query["limit"] == 2
    assert result[0]["content"] == "Documento vetorial"


@pytest.mark.parametrize(("question", "limit"), [(" ", 3), ("PDCA", 0), ("PDCA", 11)])
def test_faq_search_rejects_invalid_input(question, limit):
    with pytest.raises(ValueError):
        FaqService(Repository()).search(question, limit)
