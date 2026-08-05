from datetime import UTC, datetime

from pymongo import ReturnDocument

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError, NotFoundError
from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.serializers import serialize
from acta_mcp.modules.ciclos.repository import CiclosRepository
from acta_mcp.modules.ciclos.schemas import CausaCreate, IshikawaItemCreate
from acta_mcp.modules.common import AccessService


class CiclosService:
    def __init__(
        self,
        repository: CiclosRepository,
        mongo: MongoRepository,
        access: AccessService,
    ) -> None:
        self.repository = repository
        self.mongo = mongo
        self.access = access

    def visao_geral(self, context: RequestContext, id_ciclo: int) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        ciclo = self.repository.visao_geral(id_ciclo, context.empresa_id)
        if ciclo is None:
            raise NotFoundError(f"Nenhum ciclo encontrado com id {id_ciclo}.")
        return {
            "status": "ok",
            "ciclo": ciclo,
            "tarefas_por_status": self.repository.tarefas_por_status(
                id_ciclo,
                context.empresa_id,
            ),
            "metas_por_status": self.repository.entity_status(
                "meta",
                id_ciclo,
                context.empresa_id,
            ),
            "planos_por_status": self.repository.entity_status(
                "plano_acao",
                id_ciclo,
                context.empresa_id,
            ),
            "problemas_por_status": self.repository.entity_status(
                "problema",
                id_ciclo,
                context.empresa_id,
            ),
        }

    def problema_principal(self, context: RequestContext, id_ciclo: int) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        problema = self.repository.problema_principal(id_ciclo, context.empresa_id)
        if problema is None:
            raise NotFoundError("Nenhum problema encontrado para este ciclo.")
        return {"status": "ok", "problema_principal": problema}

    def causas_raiz(self, context: RequestContext, id_ciclo: int) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        causas = self.repository.causas_raiz(id_ciclo, context.empresa_id)
        return {"status": "ok", "count": len(causas), "causas_raiz": causas}

    def _mongo_collection(
        self,
        context: RequestContext,
        id_ciclo: int,
        collection: str,
        limit: int,
    ) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        documents = self.mongo.find_by_ciclo(
            collection=collection,
            id_ciclo=id_ciclo,
            empresa_id=context.empresa_id,
            limit=limit,
        )
        return {
            "status": "ok",
            "collection": collection,
            "id_ciclo": id_ciclo,
            "count": len(documents),
            "documentos": documents,
        }

    def ishikawa(self, context: RequestContext, id_ciclo: int, limit: int = 10) -> dict:
        return self._mongo_collection(context, id_ciclo, "ishikawa", limit)

    def riscos_pendencias(self, context: RequestContext, id_ciclo: int) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        empresa_id = context.empresa_id
        return {
            "status": "ok",
            "tarefas_em_risco_ou_pendentes": self.repository.tarefas_em_risco(
                id_ciclo,
                empresa_id,
            ),
            "metas_em_risco_ou_pendentes": self.repository.metas_em_risco(
                id_ciclo,
                empresa_id,
            ),
            "planos_de_acao_pendentes_ou_problematicos": (
                self.repository.planos_problematicos(id_ciclo, empresa_id)
            ),
            "alertas_de_prazo": self.repository.alertas(id_ciclo, empresa_id),
        }

    def treinamentos(self, context: RequestContext, id_ciclo: int) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        rows = self.repository.treinamentos(id_ciclo, context.empresa_id)
        return {"status": "ok", "count": len(rows), "treinamentos": rows}

    def participantes(self, context: RequestContext, id_ciclo: int) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        rows = self.repository.participantes(id_ciclo, context.empresa_id)
        return {"status": "ok", "count": len(rows), "participantes": rows}

    def relatorio(self, context: RequestContext, id_ciclo: int) -> dict:
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "visao_geral": self.visao_geral(context, id_ciclo),
            "problema_principal": self.problema_principal(context, id_ciclo),
            "causas_raiz": self.causas_raiz(context, id_ciclo),
            "ishikawa": self.ishikawa(context, id_ciclo),
            "riscos_pendencias": self.riscos_pendencias(context, id_ciclo),
            "treinamentos": self.treinamentos(context, id_ciclo),
            "participantes": self.participantes(context, id_ciclo),
        }

    def registrar_causa(self, context: RequestContext, **data) -> dict:
        payload = CausaCreate(**data)
        self.access.ensure_cycle(context, payload.id_ciclo)
        self.access.ensure_problem(
            context,
            payload.id_problema,
            id_ciclo=payload.id_ciclo,
        )
        if payload.id_plano_acao is not None:
            plan = self.access.ensure_plan(context, payload.id_plano_acao)
            if plan["id_ciclo"] != payload.id_ciclo:
                raise AuthorizationError("O plano de ação não pertence ao ciclo informado.")
        cause = self.repository.registrar_causa(
            id_ciclo=payload.id_ciclo,
            id_problema=payload.id_problema,
            id_plano_acao=payload.id_plano_acao,
            descricao=payload.descricao.strip(),
            aceita=payload.aceita,
            principal=payload.principal,
            usuario_id=context.usuario_id,
        )
        if cause is None:
            raise RuntimeError("A causa não foi registrada.")
        return {"status": "ok", "causa": cause}

    def adicionar_item_ishikawa(self, context: RequestContext, **data) -> dict:
        payload = IshikawaItemCreate(**data)
        self.access.ensure_cycle(context, payload.id_ciclo)
        now = datetime.now(UTC)
        document = self.mongo.database["ishikawa"].find_one_and_update(
            {
                "$and": [
                    {"id_ciclo": {"$in": [payload.id_ciclo, str(payload.id_ciclo)]}},
                    {"id_empresa": {"$in": [context.empresa_id, str(context.empresa_id)]}},
                ]
            },
            {
                "$setOnInsert": {
                    "id_ciclo": payload.id_ciclo,
                    "id_empresa": context.empresa_id,
                    "criado_por": context.usuario_id,
                    "criado_em": now,
                },
                "$addToSet": {f"causas.{payload.categoria}": payload.causa.strip()},
                "$set": {"atualizado_em": now},
            },
            upsert=True,
            return_document=ReturnDocument.AFTER,
        )
        return {"status": "ok", "ishikawa": serialize(document)}
