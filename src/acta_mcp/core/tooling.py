import logging
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from acta_mcp.core.context import get_request_context
from acta_mcp.core.exceptions import AuthorizationError, NotFoundError
from acta_mcp.core.security import AccessLevel, require_access
from acta_mcp.infrastructure.observability.audit import AuditLogger

logger = logging.getLogger(__name__)


def execute_tool(
    *,
    name: str,
    audit: AuditLogger,
    operation: Callable[[], dict[str, Any] | str],
    minimum_access: AccessLevel = "read",
) -> dict[str, Any] | str:
    context = get_request_context()
    try:
        require_access(context, minimum_access)
        return audit.execute(tool_name=name, context=context, operation=operation)
    except NotFoundError as exc:
        return {"status": "not_found", "message": str(exc), "trace_id": context.trace_id}
    except AuthorizationError as exc:
        return {"status": "forbidden", "message": str(exc), "trace_id": context.trace_id}
    except (ValidationError, ValueError) as exc:
        return {"status": "invalid_input", "message": str(exc), "trace_id": context.trace_id}
    except Exception:
        logger.exception(
            "unexpected_tool_error",
            extra={"tool_name": name, "trace_id": context.trace_id},
        )
        return {
            "status": "error",
            "message": "Não foi possível concluir a operação.",
            "trace_id": context.trace_id,
        }
