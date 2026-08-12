from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

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


class TarefaCreate(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_plano_acao: int = Field(gt=0)
    id_responsavel: int = Field(gt=0)
    titulo: str = Field(min_length=2, max_length=160)
    descricao: str = Field(min_length=2, max_length=4000)
    prioridade: Prioridade = "MEDIA"
    data_fim_prevista: date


class TarefaUpdate(BaseModel):
    id_tarefa: int = Field(gt=0)
    titulo: str | None = Field(default=None, min_length=2, max_length=160)
    descricao: str | None = Field(default=None, min_length=2, max_length=4000)
    id_responsavel: int | None = Field(default=None, gt=0)
    prioridade: Prioridade | None = None
    data_fim_prevista: date | None = None

    @model_validator(mode="after")
    def at_least_one_change(self):
        if all(
            value is None
            for value in (
                self.titulo,
                self.descricao,
                self.id_responsavel,
                self.prioridade,
                self.data_fim_prevista,
            )
        ):
            raise ValueError("Informe ao menos um campo para atualizar.")
        return self


class TarefaStatusUpdate(BaseModel):
    id_tarefa: int = Field(gt=0)
    status: TarefaStatus
