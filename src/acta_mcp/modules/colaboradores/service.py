from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import NotFoundError
from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.modules.colaboradores.repository import ColaboradoresRepository
from acta_mcp.modules.colaboradores.schemas import (
    ColaboradoresMongo,
    ColaboradoresQuery,
    RealocacaoSugestao,
)
from acta_mcp.modules.common import (
    COLABORADOR_ID_FIELDS,
    USUARIO_ID_FIELDS,
    AccessService,
    filter_documents_by_ids,
    normalize_optional_text,
)


class ColaboradoresService:
    def __init__(
        self,
        repository: ColaboradoresRepository,
        mongo: MongoRepository,
        access: AccessService,
    ) -> None:
        self.repository = repository
        self.mongo = mongo
        self.access = access

    def consultar(self, context: RequestContext, **kwargs) -> dict:
        payload = ColaboradoresQuery(**kwargs)
        if payload.id_ciclo is not None:
            self.access.ensure_cycle(context, payload.id_ciclo)
        rows = self.repository.consultar(payload, context.empresa_id)
        return {"status": "ok", "count": len(rows), "colaboradores": rows}

    def detalhes(
        self,
        context: RequestContext,
        id_colaborador: int,
        id_ciclo: int | None = None,
    ) -> dict:
        self.access.ensure_collaborator(context, id_colaborador)
        if id_ciclo is not None:
            self.access.ensure_cycle(context, id_ciclo)
        collaborator = self.repository.detalhes(id_colaborador, context.empresa_id)
        if collaborator is None:
            raise NotFoundError(f"Nenhum colaborador encontrado com id {id_colaborador}.")
        id_usuario = collaborator["id_usuario"]
        response = {
            "status": "ok",
            "colaborador": collaborator,
            "ciclos": self.repository.ciclos(id_usuario, context.empresa_id),
            "tarefas": self.repository.tarefas(
                id_usuario,
                context.empresa_id,
                id_ciclo,
            ),
            "dados_pessoais_omitidos": True,
        }
        if id_ciclo is not None:
            response.update(
                {
                    "competencias": self.competencias(
                        context,
                        id_ciclo=id_ciclo,
                        id_colaborador=id_colaborador,
                        id_usuario=id_usuario,
                    ),
                    "disponibilidade": self.disponibilidade(
                        context,
                        id_ciclo=id_ciclo,
                        id_colaborador=id_colaborador,
                        id_usuario=id_usuario,
                    ),
                    "realocacoes": self.realocacoes(
                        context,
                        id_ciclo=id_ciclo,
                        id_colaborador=id_colaborador,
                        id_usuario=id_usuario,
                    ),
                }
            )
        return response

    def participantes(self, context: RequestContext, id_ciclo: int, limit: int = 50) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        rows = self.repository.participantes(id_ciclo, context.empresa_id, limit)
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "count": len(rows),
            "participantes": rows,
        }

    def por_area(self, context: RequestContext) -> dict:
        rows = self.repository.por_area(context.empresa_id)
        return {
            "status": "ok",
            "id_empresa": context.empresa_id,
            "count": len(rows),
            "areas": rows,
        }

    def carga_trabalho(
        self,
        context: RequestContext,
        id_ciclo: int,
        limit: int = 50,
    ) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        rows = self.repository.carga_trabalho(id_ciclo, context.empresa_id, limit)
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "count": len(rows),
            "carga_trabalho": rows,
        }

    def _mongo(
        self,
        context: RequestContext,
        *,
        collection: str,
        result_field: str,
        payload: ColaboradoresMongo,
    ) -> dict:
        self.access.ensure_cycle(context, payload.id_ciclo)
        if payload.id_colaborador is not None:
            self.access.ensure_collaborator(context, payload.id_colaborador)
        documents = self.mongo.find_by_ciclo(
            collection=collection,
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            limit=payload.limit,
        )
        documents = filter_documents_by_ids(
            documents,
            (payload.id_colaborador, COLABORADOR_ID_FIELDS),
            (payload.id_usuario, USUARIO_ID_FIELDS),
        )
        return {
            "status": "ok",
            "collection": collection,
            "id_ciclo": payload.id_ciclo,
            "id_colaborador": payload.id_colaborador,
            "id_usuario": payload.id_usuario,
            "count": len(documents),
            result_field: documents,
        }

    def competencias(self, context: RequestContext, **kwargs) -> dict:
        return self._mongo(
            context,
            collection="competencias_colaborador",
            result_field="competencias",
            payload=ColaboradoresMongo(**kwargs),
        )

    def disponibilidade(self, context: RequestContext, **kwargs) -> dict:
        return self._mongo(
            context,
            collection="disponibilidade_colaborador",
            result_field="disponibilidade",
            payload=ColaboradoresMongo(**kwargs),
        )

    def realocacoes(self, context: RequestContext, **kwargs) -> dict:
        return self._mongo(
            context,
            collection="realocacoes_colaborador",
            result_field="realocacoes",
            payload=ColaboradoresMongo(**kwargs),
        )

    def sugestao_realocacao(self, context: RequestContext, **kwargs) -> dict:
        payload = RealocacaoSugestao(**kwargs)
        self.access.ensure_cycle(context, payload.id_ciclo)
        area = normalize_optional_text(payload.area)
        cargo = normalize_optional_text(payload.cargo)
        competencia = normalize_optional_text(payload.competencia)
        candidates = self.repository.candidatos_realocacao(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            area=area,
            cargo=cargo,
            limit=payload.limit,
        )
        related = {}
        for collection in (
            "competencias_colaborador",
            "disponibilidade_colaborador",
            "realocacoes_colaborador",
        ):
            related[collection] = self.mongo.find_by_ciclo(
                collection=collection,
                id_ciclo=payload.id_ciclo,
                empresa_id=context.empresa_id,
                limit=200,
            )
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "criterios": {"area": area, "cargo": cargo, "competencia": competencia},
            "candidatos_por_menor_carga": candidates,
            "competencias_registradas": related["competencias_colaborador"],
            "disponibilidade_registrada": related["disponibilidade_colaborador"],
            "realocacoes_registradas": related["realocacoes_colaborador"],
            "observacao": (
                "Candidatos são ordenados por menor carga; a decisão final deve cruzar "
                "competências, disponibilidade e validação do gestor."
            ),
        }

    def relatorio(self, context: RequestContext, id_ciclo: int, limit: int = 50) -> dict:
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "participantes": self.participantes(context, id_ciclo, limit),
            "carga_trabalho": self.carga_trabalho(context, id_ciclo, limit),
            "competencias": self.competencias(
                context,
                id_ciclo=id_ciclo,
                limit=limit,
            ),
            "disponibilidade": self.disponibilidade(
                context,
                id_ciclo=id_ciclo,
                limit=limit,
            ),
            "realocacoes": self.realocacoes(
                context,
                id_ciclo=id_ciclo,
                limit=limit,
            ),
            "sugestao_realocacao": self.sugestao_realocacao(
                context,
                id_ciclo=id_ciclo,
                limit=min(limit, 100),
            ),
        }
