from collections.abc import Iterable, Sequence
from dataclasses import replace
from typing import Any

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError, NotFoundError
from acta_mcp.core.security import current_access_level
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

    def resolve_request_context(self, context: RequestContext) -> RequestContext:
        """Deriva empresa e acesso do usuário salvo no banco, nunca do cliente."""

        row = self.postgres.fetch_one(
            """
            SELECT id, id_empresa, tipo_usuario, status
            FROM usuario_sistema
            WHERE id = %s;
            """,
            (context.usuario_id,),
        )
        if row is None:
            raise ValueError("Usuário autenticado não foi encontrado.")
        if row["status"] != "ATIVO":
            raise ValueError("Usuário autenticado não está ativo.")
        if row["id_empresa"] != context.empresa_id:
            raise ValueError("Usuário autenticado não pertence à empresa informada.")

        level_by_user_type = {
            "ADMIN": "admin",
            "GESTOR": "create",
            "COLABORADOR": "read",
        }
        level = level_by_user_type.get(row["tipo_usuario"])
        if level is None:
            raise ValueError("Tipo do usuário autenticado não é reconhecido.")
        return replace(context, permissoes=frozenset({level}))

    def ensure_cycle(self, context: RequestContext, id_ciclo: int) -> dict[str, Any]:
        row = self.postgres.fetch_one(
            """
            SELECT c.id, c.id_empresa, c.id_responsavel, uc.papel_ciclo
            FROM pdca.ciclo c
            LEFT JOIN pdca.usuario_ciclo uc
              ON uc.id_ciclo = c.id AND uc.id_usuario = %s
            WHERE c.id = %s;
            """,
            (context.usuario_id, id_ciclo),
        )
        if row is None:
            raise NotFoundError(f"Nenhum ciclo encontrado com id {id_ciclo}.")
        if row["id_empresa"] != context.empresa_id:
            raise AuthorizationError("O usuário não possui acesso a este ciclo.")
        if current_access_level(context) != "admin" and row.get("papel_ciclo") is None:
            raise AuthorizationError("O usuário não está vinculado a este ciclo.")
        return row

    def ensure_task(self, context: RequestContext, id_tarefa: int) -> None:
        row = self.postgres.fetch_one(
            """
            SELECT c.id AS id_ciclo, c.id_empresa
            FROM pdca.tarefa t
            JOIN pdca.plano_acao pa ON pa.id = t.id_plano_acao
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            WHERE t.id = %s;
            """,
            (id_tarefa,),
        )
        if row is None:
            raise NotFoundError(f"Nenhuma tarefa encontrada com id {id_tarefa}.")
        self.ensure_cycle(context, row["id_ciclo"])

    def ensure_collaborator(self, context: RequestContext, id_colaborador: int) -> None:
        row = self.postgres.fetch_one(
            "SELECT id_empresa FROM colaborador WHERE id = %s;",
            (id_colaborador,),
        )
        if row is None:
            raise NotFoundError(f"Nenhum colaborador encontrado com id {id_colaborador}.")
        if row["id_empresa"] != context.empresa_id:
            raise AuthorizationError("O usuário não possui acesso a este colaborador.")

    def ensure_user(self, context: RequestContext, usuario_id: int) -> dict[str, Any]:
        row = self.postgres.fetch_one(
            "SELECT id, id_empresa, status FROM usuario_sistema WHERE id = %s;",
            (usuario_id,),
        )
        if row is None:
            raise NotFoundError(f"Nenhum usuário encontrado com id {usuario_id}.")
        if row["id_empresa"] != context.empresa_id:
            raise AuthorizationError("O usuário informado não pertence à empresa autenticada.")
        if row.get("status") != "ATIVO":
            raise AuthorizationError("O usuário informado não está ativo.")
        return row

    def ensure_plan(self, context: RequestContext, id_plano_acao: int) -> dict[str, Any]:
        row = self.postgres.fetch_one(
            """
            SELECT pa.id, pa.id_ciclo, c.id_empresa
            FROM pdca.plano_acao pa
            JOIN pdca.ciclo c ON c.id = pa.id_ciclo
            WHERE pa.id = %s;
            """,
            (id_plano_acao,),
        )
        if row is None:
            raise NotFoundError(f"Nenhum plano de ação encontrado com id {id_plano_acao}.")
        self.ensure_cycle(context, row["id_ciclo"])
        return row

    def ensure_problem(
        self,
        context: RequestContext,
        id_problema: int,
        *,
        id_ciclo: int | None = None,
    ) -> dict[str, Any]:
        row = self.postgres.fetch_one(
            """
            SELECT p.id, p.id_ciclo, c.id_empresa
            FROM pdca.problema p
            JOIN pdca.ciclo c ON c.id = p.id_ciclo
            WHERE p.id = %s;
            """,
            (id_problema,),
        )
        if row is None:
            raise NotFoundError(f"Nenhum problema encontrado com id {id_problema}.")
        self.ensure_cycle(context, row["id_ciclo"])
        if id_ciclo is not None and row["id_ciclo"] != id_ciclo:
            raise AuthorizationError("O problema não pertence ao ciclo informado.")
        return row
