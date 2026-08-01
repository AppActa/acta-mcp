from pydantic import BaseModel, Field


class FaqQuery(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    limit: int = Field(default=3, ge=1, le=10)

