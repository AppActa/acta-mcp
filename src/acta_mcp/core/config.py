from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    acta_env: Literal["development", "test", "production"] = "development"
    acta_host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)
    acta_log_level: str = "INFO"

    acta_auth_mode: Literal["api_key", "disabled"] = "api_key"
    acta_mcp_api_key: str | None = None
    acta_default_usuario_id: int = Field(default=1, ge=1)
    acta_default_empresa_id: int = Field(default=1, ge=1)

    database_url: str = "postgresql://acta:acta@localhost:5433/acta"
    acta_postgres_pool_min_size: int = Field(default=1, ge=1)
    acta_postgres_pool_max_size: int = Field(default=10, ge=1)
    acta_postgres_timeout_seconds: float = Field(default=10, gt=0)

    mongodb_uri: str = "mongodb://localhost:27018"
    mongodb_database: str = "acta"
    acta_mongo_timeout_ms: int = Field(default=5000, ge=100)

    qdrant_api_key: str | None = None
    qdrant_cluster_endpoint: str | None = None
    qdrant_collection_name: str = "acta_faq"
    qdrant_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    qdrant_vector_size: int = Field(default=384, ge=1)
    qdrant_timeout_seconds: float = Field(default=15, gt=0)

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        if self.acta_env == "production" and self.acta_auth_mode == "disabled":
            raise ValueError("ACTA_AUTH_MODE=disabled não é permitido em produção.")
        if self.acta_auth_mode == "api_key" and not self.acta_mcp_api_key:
            raise ValueError("ACTA_MCP_API_KEY é obrigatório quando ACTA_AUTH_MODE=api_key.")
        if self.acta_postgres_pool_max_size < self.acta_postgres_pool_min_size:
            raise ValueError("O tamanho máximo do pool deve ser maior ou igual ao mínimo.")
        if self.acta_env == "production" and not self.qdrant_cluster_endpoint:
            raise ValueError("QDRANT_CLUSTER_ENDPOINT é obrigatório em produção.")
        if self.acta_env == "production" and not self.qdrant_api_key:
            raise ValueError("QDRANT_API_KEY é obrigatório em produção.")
        return self


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
