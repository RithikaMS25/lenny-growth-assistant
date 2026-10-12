
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.sources import get_db
from app.schemas.retrieval import (
    SearchRequest,
    SearchResponse,
)
from app.services.retrieval import search_chunks

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.post("", response_model=SearchResponse)
async def search_sources(
    payload: SearchRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        results = await search_chunks(
            session,
            payload.query,
            payload.limit,
        )
        return {"query": payload.query, "results": results}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
