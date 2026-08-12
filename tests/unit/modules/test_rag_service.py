from typing import Any

from acta_mcp.modules.rag.service import RagService


class FakeFaqRepository:
    def __init__(self) -> None:
        self.ensure_calls = 0
        self.queries: list[tuple[str, int]] = []

    def ensure_index(self) -> None:
        self.ensure_calls += 1

    def search(self, question: str, limit: int) -> list[dict[str, Any]]:
        self.queries.append((question, limit))
        return [
            {
                "score": 0.91,
                "source": "ACTA_DOCS::plan_ishikawa",
                "title": "Diagrama de Ishikawa",
                "section": "Plan",
                "phase": "P",
                "content": "O Ishikawa organiza causas potenciais de um problema.",
            }
        ]

    def ping(self) -> bool:
        return True


def test_search_returns_relevant_acta_document() -> None:
    repository = FakeFaqRepository()
    service = RagService(repository)  # type: ignore[arg-type]

    result = service.search("Como funciona o diagrama de Ishikawa?")
    service.search("O que são os 6M?", limit=2)

    assert result["status"] == "ok"
    assert result["count"] == 1
    assert "ishikawa" in result["resultados"][0]["content"].lower()
    assert repository.ensure_calls == 1
    assert repository.queries == [
        ("Como funciona o diagrama de Ishikawa?", 3),
        ("O que são os 6M?", 2),
    ]


def test_search_rejects_empty_question() -> None:
    service = RagService(FakeFaqRepository())  # type: ignore[arg-type]

    try:
        service.search("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("A pergunta vazia deveria ser rejeitada.")
