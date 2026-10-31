from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    top_k: int = Field(default=4, ge=1, le=20)


class Source(BaseModel):
    source: str
    page: int
    score: float
    text: str


class QueryResponse(BaseModel):
    answer: str | None = None
    sources: list[Source]
