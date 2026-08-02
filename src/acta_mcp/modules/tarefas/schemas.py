from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

TarefaStatus = Literal[
    "PENDENTE",
    "EM_ANDAMENTO",
    "BLOQUEADA",
    "CONCLUIDA",
    "ATRASADA",
    "CANCELADA",
]
Prioridade = Literal["BAIXA", "MEDIA", "ALTA", "CRITICA"]


class TarefasQuery(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_responsavel: int | None = Field(default=None, gt=0)
    status: TarefaStatus | None = None
    prioridade: Prioridade | None = None
    data_inicio: date | None = None
    data_fim: date | None = None
    apenas_atrasadas: bool = False
    limit: int = Field(default=50, ge=1, le=200)


class TarefasCiclo(BaseModel):
    id_ciclo: int = Field(gt=0)
    limit: int = Field(default=50, ge=1, le=200)


class TarefasResponsavel(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_responsavel: int | None = Field(default=None, gt=0)


class TarefasJustificativas(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_tarefa: int | None = Field(default=None, gt=0)
    limit: int = Field(default=20, ge=1, le=200)
