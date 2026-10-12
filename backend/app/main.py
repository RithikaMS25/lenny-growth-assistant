from app.api.chat import router as chat_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.api.sources import router as sources_router
from app.database import engine
from app.api.search import router as search_router
from app.api.sessions import router as sessions_router
import httpx
import os

app = FastAPI(
    title="The Lenny Growth Assistant",
    version="0.1.0",
)

# ── CORS ────────────────────────────────────────────────────────────────────
# Allow the Vite dev server (5173/5174) and any additional origins specified
# via ALLOWED_ORIGINS (comma-separated list).
_default_origins = "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173"
_allowed_origins = os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _allowed_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(chat_router)
app.include_router(sources_router)
app.include_router(sessions_router)


@app.get("/")
async def root():
    return {
        "name": "The Lenny Growth Assistant",
        "status": "running",
    }


@app.get("/health/live")
async def health_live():
    return {"status": "ok"}


@app.get("/health/ready")
async def health_ready():
    """
    Readiness probe.  Returns 200 when all critical dependencies are reachable.
    Returns 503 when any dependency is degraded.
    Never raises an unhandled 500.
    """
    checks: dict[str, str] = {
        "api": "ok",
        "database": "not_checked",
        "llm": "not_checked",
    }

    # ── Database ────────────────────────────────────────────────────────────
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except SQLAlchemyError as exc:
        checks["database"] = f"error: {type(exc).__name__}"
    except Exception as exc:  # noqa: BLE001 – catch-all for readiness probe
        checks["database"] = f"error: {type(exc).__name__}"

    # ── Ollama / LLM ─────────────────────────────────────────────────────────
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider == "openai":
        checks["llm"] = "ok" if os.getenv("OPENAI_API_KEY") else "not_configured"
    elif provider == "anthropic":
        import importlib.util
        checks["llm"] = "ok" if os.getenv("ANTHROPIC_API_KEY") and importlib.util.find_spec("claude_agent_sdk") else "not_configured"
    elif provider == "pi" and os.getenv("ENABLE_PI_PROVIDER", "false").lower() not in {"1", "true", "yes"}:
        checks["llm"] = "provider_disabled"
    elif provider == "pi" and not os.path.isfile(os.path.join(os.getenv("APPDATA", ""), "npm", "pi.ps1")):
        checks["llm"] = "pi_cli_missing"
    else:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
        model_name = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{ollama_url}/api/tags")
            if resp.status_code == 200:
                available = {m.get("name") for m in resp.json().get("models", [])}
                checks["llm"] = "ok" if model_name in available else "model_missing"
            else:
                checks["llm"] = f"http_{resp.status_code}"
        except Exception:  # noqa: BLE001
            checks["llm"] = "unreachable"

    all_ok = all(v == "ok" for v in checks.values())
    http_status = 200 if all_ok else 503

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=http_status,
        content={
            "status": "ok" if all_ok else "not_ready",
            "checks": checks,
        },
    )
