import pytest

from acta_mcp.core.auth import ActaAuthenticationMiddleware
from acta_mcp.core.config import Settings
from acta_mcp.core.context import get_request_context


async def context_app(scope, receive, send) -> None:
    context = get_request_context()
    body = f"{context.usuario_id}:{context.empresa_id}".encode()
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-length", str(len(body)).encode())],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def invoke(app, headers: dict[str, str]) -> tuple[int, bytes]:
    messages = []
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/mcp",
        "headers": [
            (key.lower().encode("latin-1"), value.encode("latin-1"))
            for key, value in headers.items()
        ],
    }

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    await app(scope, receive, send)
    status = next(message["status"] for message in messages if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return status, body


@pytest.mark.asyncio
async def test_authentication_requires_token_and_identity_headers() -> None:
    settings = Settings(
        acta_env="test",
        acta_auth_mode="api_key",
        acta_mcp_api_key="secret",
    )
    app = ActaAuthenticationMiddleware(context_app, settings)

    assert (await invoke(app, {}))[0] == 401
    assert (
        await invoke(
            app,
            {"Authorization": "Bearer secret"},
        )
    )[0] == 401

    status, body = await invoke(
        app,
        {
            "Authorization": "Bearer secret",
            "X-Acta-Usuario-Id": "7",
            "X-Acta-Empresa-Id": "3",
        },
    )
    assert status == 200
    assert body == b"7:3"

