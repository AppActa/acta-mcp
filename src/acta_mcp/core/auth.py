from collections.abc import Awaitable, Callable
from http import HTTPStatus
from typing import Any

from acta_mcp.core.config import Settings
from acta_mcp.core.context import (
    build_context,
    reset_request_context,
    set_request_context,
)
from acta_mcp.core.security import constant_time_equals, parse_positive_int

ASGIApp = Callable[
    [dict[str, Any], Callable[[], Awaitable[dict[str, Any]]], Callable[[dict[str, Any]], Awaitable[None]]],
    Awaitable[None],
]


class ActaAuthenticationMiddleware:
    """Autentica MCP HTTP sem BaseHTTPMiddleware e injeta contexto via ContextVar."""

    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        self.app = app
        self.settings = settings

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        if scope["type"] != "http" or scope.get("path") == "/health":
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        try:
            self._verify_authorization(headers)
            context = self._build_request_context(headers)
        except ValueError as exc:
            await self._reject(send, HTTPStatus.UNAUTHORIZED, str(exc))
            return

        token = set_request_context(context)
        try:
            await self.app(scope, receive, send)
        finally:
            reset_request_context(token)

    def _verify_authorization(self, headers: dict[str, str]) -> None:
        if self.settings.acta_auth_mode == "disabled":
            return

        authorization = headers.get("authorization", "")
        scheme, _, credential = authorization.partition(" ")
        if scheme.lower() != "bearer" or not credential:
            raise ValueError("Bearer token obrigatório.")
        expected = self.settings.acta_mcp_api_key or ""
        if not constant_time_equals(credential, expected):
            raise ValueError("Bearer token inválido.")

    def _build_request_context(self, headers: dict[str, str]):
        if self.settings.acta_auth_mode == "disabled":
            usuario_id = int(
                headers.get("x-acta-usuario-id", self.settings.acta_default_usuario_id)
            )
            empresa_id = int(
                headers.get("x-acta-empresa-id", self.settings.acta_default_empresa_id)
            )
        else:
            usuario_id = parse_positive_int(
                headers.get("x-acta-usuario-id"),
                header="X-Acta-Usuario-Id",
            )
            empresa_id = parse_positive_int(
                headers.get("x-acta-empresa-id"),
                header="X-Acta-Empresa-Id",
            )

        return build_context(
            usuario_id=usuario_id,
            empresa_id=empresa_id,
            permissoes=headers.get("x-acta-permissoes"),
            trace_id=headers.get("x-trace-id"),
        )

    @staticmethod
    async def _reject(send: Callable, status: HTTPStatus, message: str) -> None:
        body = f'{{"error":"{message}"}}'.encode()
        await send(
            {
                "type": "http.response.start",
                "status": int(status),
                "headers": [
                    (b"content-type", b"application/json; charset=utf-8"),
                    (b"content-length", str(len(body)).encode("ascii")),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})

