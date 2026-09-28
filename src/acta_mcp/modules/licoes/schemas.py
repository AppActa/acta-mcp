from typing import Annotated

from pydantic import BaseModel, Field

Texto = Annotated[str, Field(min_length=1, max_length=20_000)]


class LessonDraft(BaseModel):
    titulo: Annotated[str, Field(min_length=2, max_length=200)]
    licao: Texto
    categoria: Annotated[str, Field(min_length=2, max_length=100)]
    tags: list[Annotated[str, Field(min_length=1, max_length=100)]] = Field(default_factory=list, max_length=5)
