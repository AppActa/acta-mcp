from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from acta_mcp.core.context import get_request_context
from acta_mcp.core.exceptions import AuthorizationError, NotFoundError
from acta_mcp.core.security import AccessLevel, require_access


def execute_tool(
    *,
    operation: Callable[[], dict[str, Any] | str],
    minimum_access: AccessLevel = "read",
) -> dict[str, Any] | str:
    context = get_request_context()
    try:
        require_access(context, minimum_access)
        return operation()
    except NotFoundError as exc:
        return {"status": "not_found", "message": str(exc), "trace_id": context.trace_id}
    except AuthorizationError as exc:
        return {"status": "forbidden", "message": str(exc), "trace_id": context.trace_id}
    except (ValidationError, ValueError) as exc:
        return {"status": "invalid_input", "message": str(exc), "trace_id": context.trace_id}
    except Exception:
        return {
            "status": "error",
            "message": "Não foi possível concluir a operação.",
            "trace_id": context.trace_id,
        }
