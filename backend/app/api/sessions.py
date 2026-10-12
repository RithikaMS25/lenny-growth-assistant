from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.sources import get_db
from app.models import ChatSession, Message, User

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


async def _owner(session: AsyncSession):
    user = await session.scalar(select(User).where(User.email == "dev@lenny.local"))
    if user is None:
        raise HTTPException(status_code=503, detail="Development user is missing; run the seed script.")
    return user


@router.get("")
async def list_sessions(session: AsyncSession = Depends(get_db)):
    user = await _owner(session)
    rows = (await session.scalars(select(ChatSession).where(ChatSession.user_id == user.id).order_by(ChatSession.updated_at.desc()))).all()
    return [{"id": str(x.id), "title": x.title, "created_at": x.created_at.isoformat(), "updated_at": x.updated_at.isoformat()} for x in rows]


@router.get("/providers/options")
async def provider_options():
    import os
    import importlib.util
    from pathlib import Path
    pi_cli = Path(os.getenv("APPDATA", "")) / "npm" / "pi.ps1"
    return {"default": os.getenv("LLM_PROVIDER", "ollama"), "providers": [
        {"id": "ollama", "available": True, "model": os.getenv("OLLAMA_MODEL", "qwen2.5:3b")},
        {"id": "pi", "available": pi_cli.is_file() and os.getenv("ENABLE_PI_PROVIDER", "false").lower() in {"1", "true", "yes"}, "model": "Experimental · disabled after unreliable tests"},
        {"id": "openai", "available": bool(os.getenv("OPENAI_API_KEY")), "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini")},
        {"id": "anthropic", "available": bool(os.getenv("ANTHROPIC_API_KEY")) and importlib.util.find_spec("claude_agent_sdk") is not None, "model": os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")},
    ]}


@router.get("/{session_id}")
async def get_session(session_id: UUID, session: AsyncSession = Depends(get_db)):
    user = await _owner(session)
    chat = await session.scalar(select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user.id))
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    messages = (await session.scalars(select(Message).where(Message.session_id == session_id).order_by(Message.created_at, Message.id))).all()
    return {"id": str(chat.id), "title": chat.title, "messages": [{"id": str(m.id), "role": m.role, "content": m.content, "created_at": m.created_at.isoformat(), "provider": m.provider, "citations": m.citations} for m in messages]}


