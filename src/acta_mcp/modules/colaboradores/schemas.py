from typing import Literal

from pydantic import BaseModel, Field


class ColaboradoresQuery(BaseModel):
    id_ciclo: int | None = Field(default=None, gt=0)
    nome: str | None = None
    area: str | None = None
    cargo: str | None = None
    status: Literal["ATIVO", "INATIVO", "PENDENTE", "BLOQUEADO", "ARQUIVADO"] | None = None
    tipo_usuario: Literal["ADMIN", "GESTOR", "COLABORADOR"] | None = None
    permissao_gestor: bool | None = None
    limit: int = Field(default=50, ge=1, le=200)


class RealocacaoSugestao(BaseModel):
    id_ciclo: int = Field(gt=0)
    area: str | None = None
    cargo: str | None = None
    limit: int = Field(default=20, ge=1, le=100)
