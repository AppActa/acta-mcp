import logging
from collections.abc import Callable
from time import perf_counter
from typing import Any

from acta_mcp.core.context import RequestContext

logger = logging.getLogger("acta_mcp.audit")


class AuditLogger:
    def execute(
        self,
        *,
        tool_name: str,
        context: RequestContext,
        operation: Callable[[], dict[str, Any] | str],
    ) -> dict[str, Any] | str:
        started = perf_counter()
        try:
            result = operation()
        except Exception:
            logger.exception(
                "tool_failed",
                extra=self._extra(tool_name, context, started),
            )
            raise
        logger.info(
            "tool_completed",
            extra=self._extra(tool_name, context, started),
        )
        return result

    @staticmethod
    def _extra(tool_name: str, context: RequestContext, started: float) -> dict:
        return {
            "tool_name": tool_name,
            "trace_id": context.trace_id,
            "usuario_id": context.usuario_id,
            "empresa_id": context.empresa_id,
            "duration_ms": round((perf_counter() - started) * 1000, 2),
        }

