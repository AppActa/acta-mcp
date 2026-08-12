from pydantic import BaseModel, Field


class TarefaPredicao(BaseModel):
    id_tarefa: int = Field(gt=0)


class CicloPredicao(BaseModel):
    id_ciclo: int = Field(gt=0)


class TreinamentoPredicao(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_treinamento: int = Field(gt=0)


class ColaboradorPredicao(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_colaborador: int | None = Field(default=None, gt=0)


class MetaPredicao(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_meta: int | None = Field(default=None, gt=0)


class FormularioPredicao(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_formulario: str = Field(min_length=1, max_length=120)
    limit: int = Field(default=200, ge=8, le=500)


class ProblemaPredicao(BaseModel):
    id_ciclo: int = Field(gt=0)
    id_problema: int | None = Field(default=None, gt=0)
