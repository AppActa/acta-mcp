from typing import Literal

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


class FormularioCreate(BaseModel):
    id_ciclo: int = Field(gt=0)
    titulo: str = Field(min_length=2, max_length=160)
    tipo: str = Field(min_length=2, max_length=80)
    descricao: str | None = Field(default=None, max_length=2000)


class PerguntaCreate(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_formulario: str = Field(min_length=1, max_length=120)
    texto: str = Field(min_length=2, max_length=1000)
    tipo_resposta: Literal["TEXTO", "NUMERO", "DATA", "BOOLEANO", "SELECAO_UNICA", "MULTIPLA"]
    obrigatoria: bool = False
    opcoes: list[str] = Field(default_factory=list, max_length=50)


class FormularioPublish(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_formulario: str = Field(min_length=1, max_length=120)
