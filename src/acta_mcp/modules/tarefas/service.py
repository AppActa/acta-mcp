from datetime import date

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError, NotFoundError
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.tarefas.repository import TarefasRepository
from acta_mcp.modules.tarefas.schemas import (
    TarefaCreate,
    TarefasQuery,
    TarefaStatusUpdate,
    TarefaUpdate,
)


class TarefasService:
    def __init__(
        self,
        repository: TarefasRepository,
        access: AccessService,
    ) -> None:
        self.repository = repository
        self.access = access

    def consultar(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_responsavel: int | None = None,
        status: str | None = None,
        prioridade: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        apenas_atrasadas: bool = False,
        limit: int = 50,
    ) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        payload = TarefasQuery(
            id_ciclo=id_ciclo,
            id_responsavel=id_responsavel,
            status=status,
            prioridade=prioridade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            apenas_atrasadas=apenas_atrasadas,
            limit=limit,
        )
        tarefas = self.repository.consultar(payload, context.empresa_id)
        return {"status": "ok", "id_ciclo": id_ciclo, "count": len(tarefas), "tarefas": tarefas}

    def atrasadas(self, context: RequestContext, id_ciclo: int, limit: int = 50) -> dict:
        return self.consultar(
            context,
            id_ciclo=id_ciclo,
            apenas_atrasadas=True,
            limit=limit,
        )

    def concluidas(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_responsavel: int | None = None,
        prioridade: str | None = None,
        data_inicio: date | None = None,
        data_fim: date | None = None,
        limit: int = 50,
    ) -> dict:
        return self.consultar(
            context,
            id_ciclo=id_ciclo,
            id_responsavel=id_responsavel,
            status="CONCLUIDA",
            prioridade=prioridade,
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=limit,
        )

    def detalhes(self, context: RequestContext, id_tarefa: int) -> dict:
        self.access.ensure_task(context, id_tarefa)
        tarefa = self.repository.detalhes(id_tarefa, context.empresa_id)
        if tarefa is None:
            raise NotFoundError(f"Nenhuma tarefa encontrada com id {id_tarefa}.")
        return {
            "status": "ok",
            "tarefa": tarefa,
            "dependencias": self.repository.dependencias(id_tarefa, context.empresa_id),
            "tarefas_que_dependem_desta": self.repository.bloqueia(
                id_tarefa,
                context.empresa_id,
            ),
        }

    def por_responsavel(
        self,
        context: RequestContext,
        id_ciclo: int,
        id_responsavel: int | None = None,
    ) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        rows = self.repository.por_responsavel(
            id_ciclo,
            context.empresa_id,
            id_responsavel,
        )
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "count": len(rows),
            "responsaveis": rows,
        }

    def alertas(
        self,
        context: RequestContext,
        id_ciclo: int,
        somente_nao_lidos: bool = False,
    ) -> dict:
        self.access.ensure_cycle(context, id_ciclo)
        rows = self.repository.alertas(id_ciclo, context.empresa_id, somente_nao_lidos)
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "somente_nao_lidos": somente_nao_lidos,
            "count": len(rows),
            "alertas": rows,
        }

    def relatorio(self, context: RequestContext, id_ciclo: int, limit: int = 50) -> dict:
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "tarefas_gerais": self.consultar(context, id_ciclo=id_ciclo, limit=limit),
            "tarefas_atrasadas": self.atrasadas(context, id_ciclo, limit),
            "tarefas_concluidas": self.concluidas(
                context,
                id_ciclo=id_ciclo,
                limit=limit,
            ),
            "tarefas_por_responsavel": self.por_responsavel(context, id_ciclo),
            "alertas_prazo": self.alertas(context, id_ciclo),
        }

    def criar(self, context: RequestContext, **data) -> dict:
        payload = TarefaCreate(**data)
        self.access.ensure_cycle(context, payload.id_ciclo)
        plan = self.access.ensure_plan(context, payload.id_plano_acao)
        if plan["id_ciclo"] != payload.id_ciclo:
            raise AuthorizationError("O plano de ação não pertence ao ciclo informado.")
        self.access.ensure_user(context, payload.id_responsavel)
        tarefa = self.repository.criar(payload)
        if tarefa is None:
            raise RuntimeError("A tarefa não foi criada.")
        return {"status": "ok", "tarefa": tarefa}

    def atualizar(self, context: RequestContext, **data) -> dict:
        payload = TarefaUpdate(**data)
        self.access.ensure_task(context, payload.id_tarefa)
        if payload.id_responsavel is not None:
            self.access.ensure_user(context, payload.id_responsavel)
        tarefa = self.repository.atualizar(payload)
        if tarefa is None:
            raise NotFoundError(f"Nenhuma tarefa encontrada com id {payload.id_tarefa}.")
        return {"status": "ok", "tarefa": tarefa}

    def atualizar_status(self, context: RequestContext, *, id_tarefa: int, status: str) -> dict:
        payload = TarefaStatusUpdate(id_tarefa=id_tarefa, status=status)
        self.access.ensure_task(context, payload.id_tarefa)
        tarefa = self.repository.atualizar_status(payload.id_tarefa, payload.status)
        if tarefa is None:
            raise NotFoundError(f"Nenhuma tarefa encontrada com id {payload.id_tarefa}.")
        return {"status": "ok", "tarefa": tarefa}
