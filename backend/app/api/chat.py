
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.sources import get_db
from app.schemas.chat import ChatRequest, ChatResponse, Ship30Request, Ship30Response, ArtifactRequest, ArtifactResponse
from app.services.chat import (
    ChatSessionNotFoundError,
    ChatServiceError,
    answer_question,
    generate_ship30,
    generate_artifact,
)

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    session: AsyncSession = Depends(get_db),
):
    try:
        return await answer_question(
            session,
            question=payload.question,
            session_id=payload.session_id,
            limit=payload.limit,
            provider=payload.provider,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422, detail=str(exc)
        ) from exc
    except ChatSessionNotFoundError as exc:
        raise HTTPException(
            status_code=404, detail=str(exc)
        ) from exc
    except ChatServiceError as exc:
        raise HTTPException(
            status_code=503, detail=str(exc)
        ) from exc


@router.post("/ship30", response_model=Ship30Response)
async def ship30(payload: Ship30Request, session: AsyncSession = Depends(get_db)):
    try:
        return await generate_ship30(session, topic=payload.topic, provider=payload.provider, session_id=payload.session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChatServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Essay generation failed: {type(exc).__name__}") from exc


@router.post("/artifact", response_model=ArtifactResponse)
async def artifact(payload: ArtifactRequest, session: AsyncSession = Depends(get_db)):
    try:
        return await generate_artifact(session, prompt=payload.prompt, artifact_type=payload.artifact_type, provider=payload.provider, session_id=payload.session_id)
    except ChatSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ChatServiceError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Artifact generation failed: {type(exc).__name__}") from exc
