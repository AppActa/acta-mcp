from collections.abc import Callable
from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import NotFoundError
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.relatorios.schemas import ContextoRelatorio

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
        access: AccessService,
        ciclos: Any,
        tarefas: Any,
        colaboradores: Any,
        formularios: Any,
    ) -> None:
        self.access = access
        self.ciclos = ciclos
        self.tarefas = tarefas
        self.colaboradores = colaboradores
        self.formularios = formularios

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
        return _omit_sensitive(
            {
                "status": "ok",
                "id_ciclo": payload.id_ciclo,
                "somente_leitura": True,
                "ciclo": cycle,
                "tarefas": task_data,
                "equipe": team_data,
                "formularios": compact_form_summary,
            }
        )
