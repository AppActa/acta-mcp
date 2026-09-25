from threading import Lock

from acta_mcp.modules.faq.repository import FaqRepository


class FaqService:
    def __init__(self, repository: FaqRepository) -> None:
        self.repository = repository
        self._ready = False
        self._lock = Lock()

    def ensure_index(self) -> None:
        if self._ready:
            return
        with self._lock:
            if not self._ready:
                self.repository.ensure_index()
                self._ready = True

    def search(self, question: str, limit: int = 3) -> dict:
        question = question.strip()
        if not question:
            raise ValueError("A pergunta não pode ficar vazia.")
        if not 1 <= limit <= 10:
            raise ValueError("O limite deve estar entre 1 e 10.")
        self.ensure_index()
        results = self.repository.search(question, limit)
        return {"status": "ok", "count": len(results), "resultados": results}

    def ping(self) -> bool:
        return self.repository.ping()
