
from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    session_id: UUID | None = None
    limit: int = Field(default=5, ge=1, le=10)
    provider: str | None = Field(default=None, pattern="^(ollama|pi|openai|anthropic)$")


class ChatCitation(BaseModel):
    source_title: str
    source_url: str | None = None
    chunk_id: str
    similarity: float
    content: str = ""


class ChatResponse(BaseModel):
    session_id: UUID
    answer: str
    provider: str
    citations: list[ChatCitation]
    abstained: bool


class ChatSessionSummary(BaseModel):
    id: UUID
    title: str
    created_at: str
    updated_at: str


class StoredMessage(BaseModel):
    id: UUID
    role: str
    content: str
    created_at: str
    provider: str | None = None
    citations: list[dict] = Field(default_factory=list)


class Ship30Request(BaseModel):
    topic: str = Field(min_length=8, max_length=1000)
    session_id: UUID | None = None
    provider: str | None = Field(default=None, pattern="^(ollama|pi|openai|anthropic)$")


class Ship30Response(BaseModel):
    essay: str
    citations: list[ChatCitation]
    provider: str
    word_count: int
    abstained: bool


class ArtifactRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=2000)
    artifact_type: str = Field(default="markdown", pattern="^(markdown|html)$")
    provider: str | None = Field(default=None, pattern="^(ollama|pi|openai|anthropic)$")
    session_id: UUID | None = None


class ArtifactResponse(BaseModel):
    content: str
    artifact_type: str
    citations: list[ChatCitation]
    provider: str
    abstained: bool
