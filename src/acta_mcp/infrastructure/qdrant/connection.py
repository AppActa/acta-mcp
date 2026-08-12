from qdrant_client import QdrantClient

from acta_mcp.core.config import Settings


def create_qdrant_client(settings: Settings) -> QdrantClient:
    if not settings.qdrant_cluster_endpoint:
        raise ValueError("QDRANT_CLUSTER_ENDPOINT não foi configurado.")
    if not settings.qdrant_api_key:
        raise ValueError("QDRANT_API_KEY não foi configurado.")

    return QdrantClient(
        url=settings.qdrant_cluster_endpoint,
        api_key=settings.qdrant_api_key,
        timeout=settings.qdrant_timeout_seconds,
        cloud_inference=True,
    )
