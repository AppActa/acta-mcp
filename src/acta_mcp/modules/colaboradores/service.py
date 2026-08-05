from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import NotFoundError
from acta_mcp.modules.colaboradores.repository import ColaboradoresRepository
from acta_mcp.modules.colaboradores.schemas import (
    ColaboradoresQuery,
    RealocacaoSugestao,
)
from acta_mcp.modules.common import (
    AccessService,
    normalize_optional_text,
)


class ColaboradoresService:
    def __init__(
        self,
        repository: ColaboradoresRepository,
        access: AccessService,
    ) -> None:
        self.repository = repository
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
        return {
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

    def sugestao_realocacao(self, context: RequestContext, **kwargs) -> dict:
        payload = RealocacaoSugestao(**kwargs)
        self.access.ensure_cycle(context, payload.id_ciclo)
        area = normalize_optional_text(payload.area)
        cargo = normalize_optional_text(payload.cargo)
        candidates = self.repository.candidatos_realocacao(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            area=area,
            cargo=cargo,
            limit=payload.limit,
        )
        return {
            "status": "ok",
            "id_ciclo": payload.id_ciclo,
            "criterios": {"area": area, "cargo": cargo},
            "candidatos_por_menor_carga": candidates,
            "observacao": (
                "Candidatos são ordenados por menor carga de tarefas e compatibilidade "
                "de área/cargo. A decisão final deve ser validada pelo gestor."
            ),
        }

    def relatorio(self, context: RequestContext, id_ciclo: int, limit: int = 50) -> dict:
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "participantes": self.participantes(context, id_ciclo, limit),
            "carga_trabalho": self.carga_trabalho(context, id_ciclo, limit),
            "sugestao_realocacao": self.sugestao_realocacao(
                context,
                id_ciclo=id_ciclo,
                limit=min(limit, 100),
            ),
        }
