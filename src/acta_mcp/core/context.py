from contextvars import ContextVar, Token
from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class RequestContext:
    usuario_id: int
    empresa_id: int
    permissoes: frozenset[str]
    trace_id: str


_request_context: ContextVar[RequestContext | None] = ContextVar(
    "acta_request_context",
    default=None,
)


def set_request_context(context: RequestContext) -> Token:
    return _request_context.set(context)


def reset_request_context(token: Token) -> None:
    _request_context.reset(token)


def get_request_context() -> RequestContext:
    context = _request_context.get()
    if context is None:
        raise RuntimeError("Contexto autenticado não está disponível para esta requisição.")
    return context


def build_context(
    *,
    usuario_id: int,
    empresa_id: int,
    permissoes: str | None = None,
    trace_id: str | None = None,
) -> RequestContext:
    parsed_permissions = frozenset(
        permission.strip()
        for permission in (permissoes or "read").split(",")
        if permission.strip()
    )
    return RequestContext(
        usuario_id=usuario_id,
        empresa_id=empresa_id,
        permissoes=parsed_permissions,
        trace_id=trace_id or str(uuid4()),
    )

