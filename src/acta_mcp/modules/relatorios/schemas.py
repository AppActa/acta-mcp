from pydantic import BaseModel, Field


class RelatoriosQuery(BaseModel):
    id_ciclo: int = Field(gt=0)
    tipo: str | None = Field(default=None, min_length=1, max_length=80)
    formato: str | None = Field(default=None, min_length=1, max_length=20)
    status: str | None = Field(default=None, min_length=1, max_length=40)
    limit: int = Field(default=50, ge=1, le=200)


class RelatorioId(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_relatorio: str = Field(min_length=1, max_length=120)


class RelatorioMaisRecente(BaseModel):
    id_ciclo: int = Field(gt=0)
    tipo: str | None = Field(default=None, min_length=1, max_length=80)


class ContextoRelatorio(BaseModel):
    id_ciclo: int = Field(gt=0)
    limit: int = Field(default=50, ge=1, le=100)
