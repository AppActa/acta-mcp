from pydantic import BaseModel, Field


class LicaoCreate(BaseModel):
    id_ciclo: int = Field(gt=0)
    titulo: str = Field(min_length=2, max_length=200)
    licao: str = Field(min_length=3, max_length=8000)
    categoria: str | None = Field(default=None, max_length=100)
    tags: list[str] = Field(default_factory=list, max_length=30)

