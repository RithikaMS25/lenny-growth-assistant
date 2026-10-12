
from datetime import date

from pydantic import BaseModel, Field, HttpUrl


class TranscriptIngestRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    transcript: str = Field(min_length=1)
    source_type: str = Field(default="podcast")
    published_date: date | None = None
    description: str | None = None


class TranscriptIngestResponse(BaseModel):
    source_id: str
    title: str
    url: str
    chunk_count: int
