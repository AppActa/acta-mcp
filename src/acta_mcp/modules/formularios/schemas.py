from pydantic import BaseModel, Field


class FormulariosQuery(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_formulario: str | None = Field(default=None, min_length=1)
    tipo: str | None = Field(default=None, min_length=1)
    status: str | None = Field(default=None, min_length=1)
    limit: int = Field(default=50, ge=1, le=200)


class RespostasFormularioQuery(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_formulario: str | None = Field(default=None, min_length=1)
    limit: int = Field(default=100, ge=1, le=500)
