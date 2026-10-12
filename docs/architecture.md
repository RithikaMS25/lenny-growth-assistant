# Architecture and operations

## Components and data flow

The Vite React app calls FastAPI through its `/api` and `/health` development proxy. FastAPI validates schemas, stores conversations in PostgreSQL, and routes chat/essay/artifact prompts through provider adapters. Retrieval embeds each query with `all-MiniLM-L6-v2`, ranks pgvector cosine distance, then applies `RETRIEVAL_MIN_SIMILARITY`. The model sees a bounded set of evidence chunks and prior messages from that chat only. Citations are built from the same retrieved chunk IDs and metadata.

The local corpus index supplies title, optional verified publisher URL, type, date, description, and a confined relative filename. Files are chunked and embedded, then persisted with a stable chunk index. Ingestion skips existing records by URL (or title/type when no URL exists); `--refresh` replaces them. Raw corpus data is local and excluded from distribution.

## Storage

- `users`: seeded development identity.
- `chat_sessions`: owner, title, timestamps, metadata.
- `messages`: role/content/timestamp/provider/citations.
- `sources`: source metadata; URL is nullable because the supplied index has records without a publisher URL.
- `source_chunks`: source FK, chunk index, content, optional speaker/timestamps, 384-dimensional embedding.

Alembic upgrades the schema from an empty PostgreSQL database, including pgvector. Session listing/detail queries are scoped to the seeded development user. Production needs authentication, authorization, rate limiting, and operational secret management.

## APIs

See README for the route list and OpenAPI at `/docs`. Pydantic validates request bounds and provider IDs. Readiness returns 503 for an unavailable database or configured local model service. Liveness only checks the process. Errors are not converted into successful model answers.

## Provider routing

`LLM_PROVIDER` sets the default; requests can explicitly select Ollama, Pi, OpenAI, or Anthropic. Ollama is the tested local demo path. Pi is invoked in print mode with tools, MCP, session files, context files, skills, and templates disabled, using the local Ollama model, but is disabled by default after it generated off-topic output, abstained on a supported prompt, and timed out in live checks. Anthropic routes through the official Claude Agent SDK with built-in tools disabled and one turn. OpenAI uses its chat completions API. Cloud providers require their own keys. No automatic cross-provider fallback occurs, to avoid hidden cost or moving transcript data to a cloud provider unexpectedly. The SDK interface is documented at [Anthropic's Python Agent SDK](https://github.com/anthropics/claude-agent-sdk-python).

## Security and failure handling

`.env` is excluded from Git. Cloud keys are server-side only. Database and provider operations have bounded timeouts. Retrieval may abstain. HTML is untrusted and rendered in a no-script, no-same-origin sandbox with restrictive CSP; external network, forms, and scripts are blocked. This is a local assessment demo, not a production multi-user service.

## Deployment topology

PowerShell startup scripts manage the React dev server and FastAPI; Docker Compose runs a persistent pgvector PostgreSQL volume on loopback port 5433. Ollama runs as a local host service on 11434. See README for startup, migration, seed, ingestion, and stop commands.
