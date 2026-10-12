# The Lenny Growth Assistant

A local, source-grounded research workspace for exploring a private Lenny podcast/newsletter corpus, chatting with citations, drafting longer Ship 30-style essays, and previewing Markdown or HTML/CSS artifacts.

## Architecture

- React 19 + Vite frontend (`frontend/`)
- FastAPI API and provider adapters (`backend/app/`)
- PostgreSQL 16 with pgvector, managed by Alembic
- Sentence Transformers `all-MiniLM-L6-v2` embeddings and cosine similarity retrieval
- Ollama (`qwen2.5:3b`) is the default local model. OpenAI is an optional cloud adapter. Anthropic uses the Claude Agent SDK; both cloud paths need an API key. Pi Coding Agent remains opt-in because live checks against the local model produced off-topic output, abstentions on supported evidence, and a timeout.

The checked-in source does **not** contain the local corpus. The included `data/` directory is private source material and is excluded from Git and the final ZIP. Obtain and place data only where its license permits; the ingestion script expects `data/lenny-extracted/lennys-newsletterpodcastdata-main/index.json` and its referenced Markdown files.

## Prerequisites

- Windows 10/11, PowerShell, Python 3.10+, Node 22+, npm
- Docker Desktop running
- Ollama installed with `qwen2.5:3b` pulled for the local demo
- Approximately 1 GB for the Python embedding/runtime dependencies, plus model storage

## Quick start

```powershell
Copy-Item .env.example .env
ollama pull qwen2.5:3b
ollama serve   # in its own terminal, unless the Ollama app is already serving
.\scripts\start-all.ps1 -IngestCorpus
```

The first run creates `backend/.venv`, installs Python requirements, waits for PostgreSQL, runs migrations, seeds the local development identity, optionally ingests the corpus, and opens the backend and frontend in hidden PowerShell processes. Open `http://127.0.0.1:5173`. API docs are at `http://127.0.0.1:8000/docs`.

If you want to ingest separately, run `.\scripts\start-all.ps1`, then from another PowerShell window run:

```powershell
Set-Location backend
.\.venv\Scripts\python.exe scripts\ingest_corpus.py
# Re-embed and refresh indexed records after corpus changes:
.\.venv\Scripts\python.exe scripts\ingest_corpus.py --refresh
```

To start components separately, use `.\scripts\start-backend.ps1` and `.\scripts\start-frontend.ps1`. To stop PostgreSQL, run `docker compose down` from the project root. Docker volume data remains until explicitly removed.

## Configuration

Copy `.env.example` to `.env`; keep `.env` private. Local Ollama works without a cloud key.

| Variable | Purpose |
| --- | --- |
| `DATABASE_URL` | Async PostgreSQL connection string; local Compose maps port 5433 |
| `POSTGRES_PASSWORD` | Local Compose database password; change for shared environments |
| `LLM_PROVIDER` | Default `ollama`, `pi`, `openai`, or `anthropic` |
| `OLLAMA_BASE_URL`, `OLLAMA_MODEL` | Local Ollama endpoint and model |
| `RETRIEVAL_MIN_SIMILARITY` | Minimum cosine similarity accepted as grounding evidence |
| `OPENAI_API_KEY`, `OPENAI_MODEL`, `OPENAI_BASE_URL` | Optional OpenAI-compatible cloud provider |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | Optional Anthropic Messages API provider |
| `ALLOWED_ORIGINS` | Comma-separated browser origins for FastAPI CORS |
| `VITE_API_BASE_URL` | Optional separately hosted frontend API URL |

Cloud API keys are read from environment variables and never included in API responses or logs. The Claude Agent SDK runs with built-in tools disabled and a one-turn cap. Provider errors are returned as errors; the system does not pretend a failed generation succeeded or silently change providers. Pi can be explicitly re-enabled with `ENABLE_PI_PROVIDER=true` for experiments, but is disabled by default after the unsuccessful live checks.

## APIs

- `GET /health/live`, `GET /health/ready`
- `POST /api/chat`, `POST /api/chat/ship30`, `POST /api/chat/artifact`
- `GET /api/sessions`, `GET /api/sessions/{id}`, `GET /api/sessions/providers/options`
- `POST /api/search`
- `GET /api/sources`, `GET /api/sources/{id}`, `POST /api/sources/ingest`

The development identity is seeded as `dev@lenny.local`; authentication is intentionally out of scope for a local assessment demo. Do not expose this API publicly without adding real authentication and authorization.

## Tests and verification

```powershell
Set-Location backend
\.venv\Scripts\python.exe -m pytest -q
\.venv\Scripts\alembic.exe heads
Set-Location ..\frontend
npm ci
npm run build
```

`start-all.ps1` checks ports 5433, 8000, and 5173 before launching. Readiness accurately returns 503 when a critical dependency is unavailable. To check the local stack, visit `/health/ready`; then try a source search, ask a supported question, ask an unrelated question to confirm abstention, reopen a saved chat, generate an essay, and generate both Markdown and HTML artifacts.

## Artifact safety

Markdown is rendered as React text elements for a small supported subset (headings, paragraphs, lists, and bold text). HTML is rendered in a separate iframe with an empty `sandbox`, no same-origin or script permission, a restrictive Content Security Policy, and no form submission or network connections. The HTML remains untrusted even though the prompt asks the model not to emit scripts.

## Troubleshooting

- Docker unavailable: start Docker Desktop, then `docker compose up -d --wait`.
- Database unavailable: verify port 5433 and the matching `DATABASE_URL` / `POSTGRES_PASSWORD` in `.env`.
- Ollama unavailable: run `ollama serve`, check `ollama list`, and pull `qwen2.5:3b` if missing.
- Empty search results: ensure the private corpus is present, run the idempotent ingestion command, and inspect the ingestion summary.
- Cloud option disabled: add the corresponding API key to `.env`, ensure backend dependencies are installed, and restart FastAPI.
- Port conflict: stop the process using the indicated port or adjust the Compose/Uvicorn/Vite configuration consistently.

## Demo and handoff

Use [docs/demo-script.md](docs/demo-script.md) for a 2–3 minute walkthrough and [docs/manual-test-plan.md](docs/manual-test-plan.md) for a short UI check. The assignment requires an on-camera video; this repository does not claim a video was recorded or uploaded. Read [docs/architecture.md](docs/architecture.md), [docs/PRD.md](docs/PRD.md), and [docs/design.md](docs/design.md) before extending the product.
