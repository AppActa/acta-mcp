import hmac
from typing import Literal

from acta_mcp.core.context import RequestContext
from acta_mcp.core.exceptions import AuthorizationError

AccessLevel = Literal["read", "create", "geral", "admin"]
_ACCESS_RANK = {"read": 0, "create": 1, "geral": 2, "admin": 3}
_LEGACY_ACCESS = {"write": "create"}


def constant_time_equals(value: str, expected: str) -> bool:
    return hmac.compare_digest(value.encode("utf-8"), expected.encode("utf-8"))


def parse_positive_int(value: str | None, *, header: str) -> int:
    if value is None:
        raise ValueError(f"Header obrigatório ausente: {header}")
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError(f"Header inválido: {header}") from exc
    if parsed <= 0:
        raise ValueError(f"Header inválido: {header}")
    return parsed


def current_access_level(context: RequestContext) -> AccessLevel:
    """Resolve o maior nível recebido, mantendo `write` como alias legado de `create`."""

    normalized = {
        _LEGACY_ACCESS.get(permission.strip().lower(), permission.strip().lower())
        for permission in context.permissoes
    }
    valid = [level for level in _ACCESS_RANK if level in normalized]
    return max(valid, key=_ACCESS_RANK.__getitem__) if valid else "read"


def require_access(context: RequestContext, minimum: AccessLevel) -> None:
    current = current_access_level(context)
    if _ACCESS_RANK[current] < _ACCESS_RANK[minimum]:
        raise AuthorizationError(
            f"Esta operação exige nível de acesso '{minimum}'. Nível atual: '{current}'."
        )
