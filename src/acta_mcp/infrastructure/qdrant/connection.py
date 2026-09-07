from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient

from acta_mcp.core.config import Settings, get_settings

EMBEDDING_MODEL = "gemini-embedding-2-preview"
EMBEDDING_DIM = 768


def create_qdrant_client(settings: Settings) -> QdrantClient:
    if not settings.qdrant_cluster_endpoint:
        raise ValueError("QDRANT_CLUSTER_ENDPOINT não foi configurado.")
    if not settings.qdrant_api_key:
        raise ValueError("QDRANT_API_KEY não foi configurado.")

    return QdrantClient(
        url=settings.qdrant_cluster_endpoint,
        api_key=settings.qdrant_api_key,
        timeout=settings.qdrant_timeout_seconds,
        cloud_inference=False,
    )


@lru_cache(maxsize=1)
def _embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=api_key)


def _gemini_api_key() -> str:
    api_key = get_settings().gemini_api_key
    if not api_key:
        raise ValueError("GEMINI_API_KEY não foi configurada.")
    return api_key


def gerar_embedding(texto: str) -> list[float]:
    """Gera um vetor Gemini de 768 dimensões para um texto."""
    return _embeddings(_gemini_api_key()).embed_query(
        texto, output_dimensionality=EMBEDDING_DIM
    )


def gerar_embeddings_batch(textos: list[str]) -> list[list[float]]:
    """Gera vetores Gemini de 768 dimensões em lote."""
    if not textos:
        return []
    return _embeddings(_gemini_api_key()).embed_documents(
        textos, output_dimensionality=EMBEDDING_DIM
    )
