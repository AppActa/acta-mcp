from pydantic import BaseModel, Field


class CicloId(BaseModel):
    id_ciclo: int = Field(gt=0)


class CicloMongo(BaseModel):
    id_ciclo: int = Field(gt=0)
    limit: int = Field(default=10, ge=1, le=200)
