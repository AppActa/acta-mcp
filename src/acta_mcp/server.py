from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from acta_mcp.container import Container
from acta_mcp.core.auth import ActaAuthenticationMiddleware
from acta_mcp.core.config import Settings
from acta_mcp.infrastructure.mongodb.base_repository import MongoRepository
from acta_mcp.infrastructure.mongodb.connection import create_mongo_client
from acta_mcp.infrastructure.observability.audit import AuditLogger
from acta_mcp.infrastructure.observability.otel import instrument_asgi_app
from acta_mcp.infrastructure.postgres.base_repository import PostgresRepository
from acta_mcp.infrastructure.postgres.connection import create_postgres_pool
from acta_mcp.infrastructure.qdrant.connection import create_qdrant_client
from acta_mcp.modules.ciclos.repository import CiclosRepository
from acta_mcp.modules.ciclos.service import CiclosService
from acta_mcp.modules.colaboradores.repository import ColaboradoresRepository
from acta_mcp.modules.colaboradores.service import ColaboradoresService
from acta_mcp.modules.common import AccessService
from acta_mcp.modules.formularios.repository import FormulariosRepository
from acta_mcp.modules.formularios.service import FormulariosService
from acta_mcp.modules.memoria.repository import MemoryRepository
from acta_mcp.modules.memoria.service import MemoryService
from acta_mcp.modules.predicoes.repository import PredicoesRepository
from acta_mcp.modules.predicoes.service import PredicoesService
from acta_mcp.modules.rag.repository import FaqRepository
from acta_mcp.modules.rag.service import RagService
from acta_mcp.modules.relatorios.service import RelatoriosService
from acta_mcp.modules.skills.repository import SkillsRepository
from acta_mcp.modules.skills.service import SkillsService
from acta_mcp.modules.tarefas.repository import TarefasRepository
from acta_mcp.modules.tarefas.service import TarefasService
from acta_mcp.modules.treinamentos.repository import TreinamentosRepository
from acta_mcp.modules.treinamentos.service import TreinamentosService
from acta_mcp.registry import register_all


def create_container(settings: Settings) -> Container:
    postgres_pool = create_postgres_pool(settings)
    mongo_client = create_mongo_client(settings)
    qdrant_client = create_qdrant_client(settings)
    postgres = PostgresRepository(postgres_pool)
    mongo = MongoRepository(mongo_client[settings.mongodb_database])
    access = AccessService(postgres)
    container = Container(
        settings=settings,
        postgres_pool=postgres_pool,
        mongo_client=mongo_client,
        qdrant_client=qdrant_client,
        postgres=postgres,
        mongo=mongo,
        access=access,
        audit=AuditLogger(),
    )
    container.ciclos = CiclosService(CiclosRepository(postgres), mongo, access)
    container.tarefas = TarefasService(TarefasRepository(postgres), access)
    container.colaboradores = ColaboradoresService(
        ColaboradoresRepository(postgres),
        access,
    )
    container.formularios = FormulariosService(FormulariosRepository(mongo), access)
    container.memoria = MemoryService(
        MemoryRepository(
            mongo.database,
            qdrant_client,
            messages_collection_name=settings.qdrant_memory_messages_collection_name,
            memories_collection_name=settings.qdrant_memory_collection_name,
            vector_size=settings.qdrant_memory_vector_size,
            message_retention_days=settings.acta_memory_message_retention_days,
            inferred_retention_days=settings.acta_memory_inferred_retention_days,
        ),
        recent_messages=settings.acta_memory_recent_messages,
        summary_every_messages=settings.acta_memory_summary_every_messages,
    )
    container.relatorios = RelatoriosService(
        access,
        container.ciclos,
        container.tarefas,
        container.colaboradores,
        container.formularios,
    )
    container.predicoes = PredicoesService(PredicoesRepository(postgres, mongo), access)
    container.rag = RagService(
        FaqRepository(
            qdrant_client,
            collection_name=settings.qdrant_collection_name,
            embedding_model=settings.qdrant_embedding_model,
            vector_size=settings.qdrant_vector_size,
        )
    )
    container.skills = SkillsService(SkillsRepository(mongo.database))
    container.treinamentos = TreinamentosService(TreinamentosRepository(postgres), access)
    return container


def create_mcp_server(settings: Settings, container: Container) -> FastMCP:
    @asynccontextmanager
    async def lifespan(_: FastMCP) -> AsyncIterator[Container]:
        # Em HTTP stateless este lifespan é criado por requisição. Recursos de
        # processo são gerenciados no lifespan ASGI em create_http_app().
        yield container

    mcp = FastMCP(
        name="ACTA MCP",
        instructions=(
            "Operações seguras e estruturadas do ACTA. A empresa e o usuário são "
            "determinados pelo contexto autenticado, nunca por argumentos do modelo."
        ),
        lifespan=lifespan,
        stateless_http=True,
        json_response=True,
        host=settings.acta_host,
        port=settings.port,
    )
    register_all(mcp, container)
    return mcp


def create_http_app(settings: Settings, mcp: FastMCP, container: Container):
    async def health(_: Request) -> JSONResponse:
        checks: dict[str, bool] = {}
        try:
            checks["postgres"] = container.postgres.ping()
        except Exception:
            checks["postgres"] = False
        try:
            checks["mongodb"] = container.mongo.ping()
        except Exception:
            checks["mongodb"] = False
        try:
            checks["qdrant"] = container.rag.ping()
        except Exception:
            checks["qdrant"] = False
        healthy = all(checks.values())
        return JSONResponse(
            {
                "status": "ok" if healthy else "degraded",
                "service": "acta-mcp",
                "checks": checks,
            },
            status_code=200 if healthy else 503,
        )

    app = mcp.streamable_http_app()
    app.routes.insert(0, Route("/health", endpoint=health, methods=["GET"]))
    mcp_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def application_lifespan(starlette_app):
        container.postgres_pool.open(wait=True)
        container.postgres.ping()
        container.mongo.ping()
        container.memoria.ensure_indexes()
        container.rag.ensure_index()
        container.skills.ensure_indexes()
        try:
            async with mcp_lifespan(starlette_app):
                yield
        finally:
            container.close()

    app.router.lifespan_context = application_lifespan
    app = ActaAuthenticationMiddleware(
        app,
        settings,
        context_resolver=container.access.resolve_request_context,
    )
    return instrument_asgi_app(app)


def build_application(settings: Settings):
    container = create_container(settings)
    mcp = create_mcp_server(settings, container)
    app = create_http_app(settings, mcp, container)
    return mcp, app, container
