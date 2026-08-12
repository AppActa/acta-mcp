from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from acta_mcp.core.context import RequestContext
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.licoes_aprendidas.repository import LicoesAprendidasRepository
from acta_mcp.modules.licoes_aprendidas.schemas import LicaoCreate


class LicoesAprendidasService:
    def __init__(self, repository: LicoesAprendidasRepository, access: AccessService) -> None:
        self.repository = repository
        self.access = access

    def ensure_indexes(self) -> None:
        self.repository.ensure_indexes()

    def registrar(self, context: RequestContext, **data) -> dict[str, Any]:
        payload = LicaoCreate(**data)
        self.access.ensure_cycle(context, payload.id_ciclo)
        tags = list(dict.fromkeys(tag.strip().lower() for tag in payload.tags if tag.strip()))
        document = {
            "_id": str(uuid4()),
            "id_licao": str(uuid4()),
            "id_ciclo": payload.id_ciclo,
            "id_empresa": context.empresa_id,
            "titulo": payload.titulo.strip(),
            "licao": payload.licao.strip(),
            "categoria": payload.categoria.strip().upper() if payload.categoria else None,
            "tags": tags,
            "criado_por": context.usuario_id,
            "criado_em": datetime.now(UTC),
        }
        return {"status": "ok", "licao_aprendida": self.repository.criar(document)}

