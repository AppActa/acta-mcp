from datetime import date

from pydantic import BaseModel, Field


class TreinamentoCreate(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_responsavel: int = Field(gt=0)
    titulo: str = Field(min_length=2, max_length=160)
    descricao: str | None = Field(default=None, max_length=4000)
    data_treinamento: date
    obrigatorio: bool = True
    participantes: list[int] = Field(default_factory=list, max_length=500)

