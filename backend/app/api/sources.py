
from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.schemas.ingestion import (
    TranscriptIngestRequest,
    TranscriptIngestResponse,
)
from app.services.ingestion import ingest_transcript
from app.models import Source, SourceChunk

router = APIRouter(prefix="/api/sources", tags=["Sources"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("")
async def list_sources(session: AsyncSession = Depends(get_db)):
    rows = (await session.execute(select(Source, func.count(SourceChunk.id).label("chunks")).outerjoin(SourceChunk, SourceChunk.source_id == Source.id).group_by(Source.id).order_by(Source.title))).all()
    return [{"id": str(source.id), "title": source.title, "source_type": source.source_type, "url": source.url, "published_date": source.published_date.isoformat() if source.published_date else None, "chunk_count": chunks} for source, chunks in rows]


@router.get("/{source_id}")
async def get_source(source_id: UUID, session: AsyncSession = Depends(get_db)):
    source = await session.get(Source, source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    chunks = (await session.scalars(select(SourceChunk).where(SourceChunk.source_id == source_id).order_by(SourceChunk.chunk_index))).all()
    return {"id": str(source.id), "title": source.title, "source_type": source.source_type, "url": source.url, "published_date": source.published_date.isoformat() if source.published_date else None, "description": source.description, "chunks": [{"id": str(chunk.id), "index": chunk.chunk_index, "content": chunk.content} for chunk in chunks]}


@router.post(
    "/ingest",
    response_model=TranscriptIngestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ingest_source(
    payload: TranscriptIngestRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        result = await ingest_transcript(
            session,
            title=payload.title,
            url=str(payload.url),
            transcript=payload.transcript,
            source_type=payload.source_type,
            published_date=payload.published_date,
            description=payload.description,
        )
        return result
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT
            if "already exists" in str(exc)
            else status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A source with this URL already exists.",
        ) from exc
