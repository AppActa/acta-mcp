from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.treinamentos.repository import TreinamentosRepository
from acta_mcp.modules.treinamentos.schemas import TreinamentoCreate


class TreinamentosService:
    def __init__(self, repository: TreinamentosRepository, access: AccessService) -> None:
        self.repository = repository
        self.access = access

    def criar(self, context: RequestContext, **data) -> dict[str, Any]:
        payload = TreinamentoCreate(**data)
        self.access.ensure_cycle(context, payload.id_ciclo)
        self.access.ensure_user(context, payload.id_responsavel)
        participants = list(dict.fromkeys(payload.participantes))
        for user_id in participants:
            self.access.ensure_user(context, user_id)
        payload = payload.model_copy(update={"participantes": participants})
        return {"status": "ok", "treinamento": self.repository.criar(payload)}

