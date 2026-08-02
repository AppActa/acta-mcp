from collections.abc import Callable
from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import NotFoundError
from acta_mcp.modules.common import AccessService, normalize_optional_text
from acta_mcp.modules.relatorios.repository import RelatoriosRepository
from acta_mcp.modules.relatorios.schemas import (
    ContextoRelatorio,
    RelatorioId,
    RelatorioMaisRecente,
    RelatoriosQuery,
)

_SENSITIVE_FIELDS = {
    "cnpj",
    "cpf",
    "senha",
    "senha_hash",
    "email",
    "email_login",
    "email_responsavel",
    "email_usuario",
    "email_usuario_destino",
}


def _normalize_filter(value: str | None) -> str | None:
    return normalize_optional_text(value, uppercase=True)


def _omit_sensitive(value: Any) -> Any:
    if isinstance(value, list):
        return [_omit_sensitive(item) for item in value]
    if isinstance(value, dict):
        return {
            key: _omit_sensitive(item)
            for key, item in value.items()
            if key.casefold() not in _SENSITIVE_FIELDS
        }
    return value


def _optional_source(operation: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        return operation()
    except NotFoundError as error:
        return {"status": "sem_dados", "motivo": str(error)}


class RelatoriosService:
    def __init__(
        self,
        repository: RelatoriosRepository,
        access: AccessService,
        ciclos: Any,
        tarefas: Any,
        colaboradores: Any,
        formularios: Any,
    ) -> None:
        self.repository = repository
        self.access = access
        self.ciclos = ciclos
        self.tarefas = tarefas
        self.colaboradores = colaboradores
        self.formularios = formularios

    def ensure_indexes(self) -> None:
        self.repository.ensure_indexes()

    def listar(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        tipo: str | None = None,
        formato: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        self.access.ensure_cycle(context, id_ciclo)
        query = RelatoriosQuery(
            id_ciclo=id_ciclo,
            tipo=_normalize_filter(tipo),
            formato=_normalize_filter(formato),
            status=_normalize_filter(status),
            limit=limit,
        )
        reports = self.repository.listar(
            id_ciclo=query.id_ciclo,
            empresa_id=context.empresa_id,
            tipo=query.tipo,
            formato=query.formato,
            status=query.status,
            limit=query.limit,
        )
        return {
            "status": "ok",
            "collection": "relatorios",
            "id_ciclo": id_ciclo,
            "count": len(reports),
            "relatorios": _omit_sensitive(reports),
        }

    def detalhes(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        id_relatorio: str,
    ) -> dict[str, Any]:
        self.access.ensure_cycle(context, id_ciclo)
        payload = RelatorioId(id_ciclo=id_ciclo, id_relatorio=id_relatorio)
        report = self.repository.obter(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            id_relatorio=payload.id_relatorio,
        )
        if report is None:
            raise NotFoundError(f"Nenhum relatório autorizado encontrado com id {id_relatorio}.")
        return {"status": "ok", "relatorio": _omit_sensitive(report)}

    def mais_recente(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        tipo: str | None = None,
    ) -> dict[str, Any]:
        self.access.ensure_cycle(context, id_ciclo)
        payload = RelatorioMaisRecente(
            id_ciclo=id_ciclo,
            tipo=_normalize_filter(tipo),
        )
        report = self.repository.mais_recente(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            tipo=payload.tipo,
        )
        if report is None:
            return {
                "status": "ok",
                "id_ciclo": id_ciclo,
                "encontrado": False,
                "relatorio": None,
            }
        return {
            "status": "ok",
            "id_ciclo": id_ciclo,
            "encontrado": True,
            "relatorio": _omit_sensitive(report),
        }

    def contexto_ciclo(
        self,
        context: RequestContext,
        *,
        id_ciclo: int,
        limit: int = 50,
    ) -> dict[str, Any]:
        payload = ContextoRelatorio(id_ciclo=id_ciclo, limit=limit)
        self.access.ensure_cycle(context, payload.id_ciclo)

        cycle = {
            "visao_geral": self.ciclos.visao_geral(context, payload.id_ciclo),
            "problema_principal": _optional_source(
                lambda: self.ciclos.problema_principal(context, payload.id_ciclo)
            ),
            "causas_raiz": self.ciclos.causas_raiz(context, payload.id_ciclo),
            "ishikawa": self.ciclos.ishikawa(context, payload.id_ciclo, 10),
            "riscos_pendencias": self.ciclos.riscos_pendencias(context, payload.id_ciclo),
            "treinamentos": self.ciclos.treinamentos(context, payload.id_ciclo),
        }
        task_data = self.tarefas.relatorio(context, payload.id_ciclo, payload.limit)
        team_data = {
            "participantes": self.colaboradores.participantes(
                context, payload.id_ciclo, payload.limit
            ),
            "carga_trabalho": self.colaboradores.carga_trabalho(
                context, payload.id_ciclo, payload.limit
            ),
        }
        form_summary = self.formularios.resumo_respostas(
            context,
            id_ciclo=payload.id_ciclo,
            limit=min(payload.limit * 4, 200),
        )
        compact_form_summary = {
            key: value
            for key, value in form_summary.items()
            if key not in {"formularios", "respostas"}
        }
        stored = self.repository.listar(
            id_ciclo=payload.id_ciclo,
            empresa_id=context.empresa_id,
            tipo=None,
            formato=None,
            status=None,
            limit=10,
        )
        return _omit_sensitive(
            {
                "status": "ok",
                "id_ciclo": payload.id_ciclo,
                "somente_leitura": True,
                "ciclo": cycle,
                "tarefas": task_data,
                "equipe": team_data,
                "formularios": compact_form_summary,
                "relatorios_existentes": stored,
            }
        )
