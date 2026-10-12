
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Source, SourceChunk
from app.services.embeddings import embed_query


def extract_requested_speaker(query: str) -> str | None:
    """Extract a speaker from 'According to Molly Graham...' questions."""
    match = re.search(
        r"\baccording to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})",
        query,
        flags=re.IGNORECASE,
    )
    if not match:
        return None
    return match.group(1).strip()


async def search_chunks(
    session: AsyncSession,
    query: str,
    limit: int = 5,
) -> list[dict]:
    """Retrieve relevant chunks, prioritizing a requested speaker."""

    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")
    if not 1 <= limit <= 20:
        raise ValueError("limit must be between 1 and 20")

    query_vector = embed_query(query)
    distance = SourceChunk.embedding.cosine_distance(query_vector)

    statement = (
        select(
            SourceChunk.id,
            SourceChunk.content,
            SourceChunk.chunk_index,
            Source.title,
            Source.url,
            Source.source_type,
            distance.label("distance"),
        )
        .join(Source, Source.id == SourceChunk.source_id)
        .where(SourceChunk.embedding.is_not(None))
        .order_by(distance)
        .limit(max(limit * 4, 20))
    )

    result = await session.execute(statement)
    rows = result.all()

    results = [
        {
            "chunk_id": str(row.id),
            "content": row.content,
            "chunk_index": row.chunk_index,
            "source_title": row.title,
            "source_url": row.url,
            "source_type": row.source_type,
            "similarity": round(1.0 - float(row.distance), 4),
        }
        for row in rows
    ]

    speaker = extract_requested_speaker(query)
    if speaker:
        pattern = re.compile(
            rf"(?<!\w){re.escape(speaker)}(?!\w)",
            re.IGNORECASE,
        )
        matching = [
            item for item in results
            if pattern.search(item["content"])
        ]
        other = [
            item for item in results
            if not pattern.search(item["content"])
        ]
        results = matching + other

    return results[:limit]
