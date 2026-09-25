from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from acta_mcp.core.config import Settings

MODEL = "gemini-embedding-2-preview"
VECTOR_SIZE = 768


@lru_cache(maxsize=2)
def _embeddings(api_key: str) -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(model=MODEL, google_api_key=api_key)


def embed_query(settings: Settings, text: str) -> list[float]:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada para busca FAQ semântica.")
    return _embeddings(settings.gemini_api_key).embed_query(
        text, output_dimensionality=VECTOR_SIZE
    )


def embed_documents(settings: Settings, texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY não configurada para indexar FAQ semântica.")
    return _embeddings(settings.gemini_api_key).embed_documents(
        texts, output_dimensionality=VECTOR_SIZE
    )
