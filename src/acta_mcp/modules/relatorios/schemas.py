from pydantic import BaseModel, Field


class ContextoRelatorio(BaseModel):
    id_ciclo: int = Field(gt=0)
    limit: int = Field(default=50, ge=1, le=100)
