
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Source, SourceChunk
from app.services.chunking import chunk_text
from app.services.embeddings import embed_texts


async def ingest_transcript(
    session: AsyncSession,
    *,
    title: str,
    url: str | None,
    transcript: str,
    source_type: str = "podcast",
    published_date: date | None = None,
    description: str | None = None,
) -> dict:
    """Persist a transcript, its chunks, and their embeddings."""

    title = title.strip()
    url = url.strip() or None if url else None
    transcript = transcript.strip()
    source_type = source_type.strip().lower()

    if not title:
        raise ValueError("title is required")
    if not transcript:
        raise ValueError("transcript is required")
    if source_type not in {"podcast", "newsletter", "article"}:
        raise ValueError("unsupported source_type")

    existing = await session.scalar(
        select(Source).where(Source.url == url)
    )
    if existing is not None:
        raise ValueError("A source with this URL already exists")

    chunks = chunk_text(transcript)
    if not chunks:
        raise ValueError("transcript contains no usable text")

    # Generate vectors before writing to the database.
    vectors = embed_texts([chunk.content for chunk in chunks])

    try:
        source = Source(
            source_type=source_type,
            title=title,
            url=url,
            published_date=published_date,
            description=description,
        )
        session.add(source)
        await session.flush()

        rows = [
            SourceChunk(
                source_id=source.id,
                chunk_index=chunk.index,
                content=chunk.content,
                embedding=vectors[chunk.index],
            )
            for chunk in chunks
        ]
        session.add_all(rows)
        await session.commit()

        return {
            "source_id": str(source.id),
            "title": source.title,
            "url": source.url,
            "chunk_count": len(rows),
        }
    except Exception:
        await session.rollback()
        raise
