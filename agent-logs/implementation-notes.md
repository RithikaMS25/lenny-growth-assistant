# Sanitized implementation notes

- Initial inspection found an existing FastAPI/React application, three migrations, 18 eventual backend tests, and 60 indexed local source records. No Git repository/remote was present in the workspace.
- The first corrected check invocation used the wrong working directory; it was rerun from the backend and frontend directories.
- The existing readiness test hard-coded a healthy response while dependencies could be unavailable. It now tests both dependency success and database failure with stubs; readiness itself reports current dependency status.
- Corpus audit showed 29 records lacked a publisher URL but all referenced Markdown files existed. URL absence is now represented as SQL `NULL`; ingestion and citation UI do not invent a publisher link.
- A first live ingestion attempt found empty strings were not normalized to `NULL`, causing the unique source URL constraint to reject records. The run was stopped, the normalization was corrected, and ingestion then completed with zero failures.
- Pi's installed Windows launcher was `pi.ps1`, not `pi.cmd`. The wrapper path was corrected and subprocess success/failure behavior has automated coverage.
- Runtime services available for verification: PostgreSQL accepted the schema upgrade and corpus ingestion. The Ollama model was started and produced one relevant answer with three real citations. Pi produced off-topic text once, abstained on a supported question once, and timed out once; it is disabled by default. The Claude Agent SDK adapter is configured with tools disabled, but no Anthropic key was available for a live cloud call. Docker Desktop was unavailable.

No transcript body, API key, database password, or model output is recorded in this log.
