from collections.abc import Iterable, Sequence
from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError, NotFoundError
from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository

TAREFA_ID_FIELDS = ("id_tarefa", "tarefa_id", "idTarefa", "tarefaId")
COLABORADOR_ID_FIELDS = (
    "id_colaborador",
    "colaborador_id",
    "idColaborador",
    "colaboradorId",
)
USUARIO_ID_FIELDS = ("id_usuario", "usuario_id", "idUsuario", "usuarioId")


def normalize_optional_text(value: str | None, *, uppercase: bool = False) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized.upper() if uppercase else normalized


def normalize_limit(limit: int | None, default: int = 50, maximum: int = 200) -> int:
    normalized = limit if limit is not None else default
    if normalized <= 0:
        return default
    return min(normalized, maximum)


def filter_documents_by_ids(
    documents: list[dict],
    *identifier_filters: tuple[Any | None, Sequence[str]],
) -> list[dict]:
    active_filters: list[tuple[str, Iterable[str]]] = [
        (str(identifier), field_names)
        for identifier, field_names in identifier_filters
        if identifier is not None
    ]
    if not active_filters:
        return documents
    return [
        document
        for document in documents
        if all(
            expected_id
            in {
                str(document[field_name])
                for field_name in field_names
                if document.get(field_name) is not None
            }
            for expected_id, field_names in active_filters
        )
    ]


class AccessService:
    def __init__(self, postgres: PostgresRepository) -> None:
        self.postgres = postgres

    def ensure_cycle(self, context: RequestContext, id_ciclo: int) -> None:
        row = self.postgres.fetch_one(
            "SELECT id_empresa FROM pdca.ciclo WHERE id = %s;",
            (id_ciclo,),
        )
        if row is None:
            raise NotFoundError(f"Nenhum ciclo encontrado com id {id_ciclo}.")
        if row["id_empresa"] != context.empresa_id:
            raise AuthorizationError("O usuário não possui acesso a este ciclo.")

    def ensure_task(self, context: RequestContext, id_tarefa: int) -> None:
        row = self.postgres.fetch_one(
            """
            SELECT c.id_empresa
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            WHERE t.id = %s;
            """,
            (id_tarefa,),
        )
        if row is None:
            raise NotFoundError(f"Nenhuma tarefa encontrada com id {id_tarefa}.")
        if row["id_empresa"] != context.empresa_id:
            raise AuthorizationError("O usuário não possui acesso a esta tarefa.")

    def ensure_collaborator(self, context: RequestContext, id_colaborador: int) -> None:
        row = self.postgres.fetch_one(
            "SELECT id_empresa FROM colaborador WHERE id = %s;",
            (id_colaborador,),
        )
        if row is None:
            raise NotFoundError(f"Nenhum colaborador encontrado com id {id_colaborador}.")
        if row["id_empresa"] != context.empresa_id:
            raise AuthorizationError("O usuário não possui acesso a este colaborador.")

