
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    limit: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    chunk_id: str
    content: str
    chunk_index: int
    source_title: str
    source_url: str | None = None
    source_type: str
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
