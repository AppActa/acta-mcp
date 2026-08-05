from typing import Literal

from pydantic import BaseModel, Field


class CicloId(BaseModel):
    id_ciclo: int = Field(gt=0)


class CicloMongo(BaseModel):
    id_ciclo: int = Field(gt=0)
    limit: int = Field(default=10, ge=1, le=200)


class CausaCreate(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_problema: int = Field(gt=0)
    descricao: str = Field(min_length=3, max_length=4000)
    id_plano_acao: int | None = Field(default=None, gt=0)
    aceita: bool = False
    principal: bool = False


class IshikawaItemCreate(BaseModel):
    id_ciclo: int = Field(gt=0)
    categoria: Literal[
        "metodo",
        "mao_de_obra",
        "maquina",
        "material",
        "medicao",
        "meio_ambiente",
    ]
    causa: str = Field(min_length=3, max_length=1000)
