from threading import Lock

from acta_mcp.modules.rag.documents import ACTA_DOCS
from acta_mcp.modules.rag.repository import FaqRepository
from acta_mcp.modules.rag.schemas import FaqQuery


class RagService:
    def __init__(self, repository: FaqRepository) -> None:
        self.repository = repository
        self._ready = False
        self._ready_lock = Lock()

    def ensure_index(self) -> None:
        if self._ready:
            return
        with self._ready_lock:
            if self._ready:
                return
            self.repository.ensure_index()
            self._ready = True

    def search(self, question: str, limit: int = 3) -> dict:
        payload = FaqQuery(question=question.strip(), limit=limit)
        self.ensure_index()
        results = self.repository.search(payload.question, payload.limit)
        return {"status": "ok", "count": len(results), "resultados": results}

    def ping(self) -> bool:
        return self.repository.ping()

    def documentation(self) -> list[dict]:
        return ACTA_DOCS
