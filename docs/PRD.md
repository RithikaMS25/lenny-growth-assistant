# Product requirements: Lenny Growth Assistant

## Discovery brief

- **Primary user:** a product or growth practitioner who wants to apply lessons from Lenny's Podcast and Newsletter to a current decision.
- **Job and pain:** find useful advice across a large transcript library, understand the evidence behind it, and turn it into a reusable written artifact without manually searching many files or trusting uncited model output.
- **Success measures (targets, not measured results):** at least 90% of supported demo answers include a valid indexed source citation; unsupported questions abstain; a new evaluator can launch the local stack using the documented workflow in under 15 minutes after dependencies and corpus are present. Measure with a labeled acceptance set before claiming achieved.
- **Assumptions:** one local development user is enough for the assessment; source files are supplied locally and may be subject to redistribution restrictions; Ollama is the mandatory demo path; local model quality is lower than a configured cloud model; citation URLs are optional when the source repository has no verified publisher URL.
- **Included:** retrieval, citations, abstention, persistence/history, source search/details, provider selection, Ship 30 essay generation, Markdown/HTML artifacts, local startup and handoff documentation.
- **Excluded:** public deployment, production authentication, multi-tenant access control, billing, and automatic downloading/redistribution of copyrighted source data. These need client decisions and credentials.
- **Risks and trade-offs:** retrieval misses and false matches; model latency/quality; optional cloud cost and data egress; private transcript leakage; stale corpus; unsafe HTML; local-only identity. Mitigations include evidence thresholds, citations, explicit abstention, local default, secret-safe configuration, refreshable indexing, iframe isolation, and a documented non-production boundary. Pi's installed CLI was tested live but disabled by default after unreliable answer quality/timeouts; the optional cloud agent path uses Anthropic's SDK.

## Journeys and acceptance criteria

1. **Ask and follow up:** user asks a product/growth question, sees an answer with source citations, asks a follow-up in the same session, and can revisit that session later. Unsupported evidence yields an explicit abstention.
2. **Search sources:** user searches the local vector index, sees ranked chunk relevance, source type, title, and a link only where a real URL exists; source details expose indexed chunks.
3. **Choose a provider:** the UI displays available providers and selected model; unconfigured cloud providers are disabled; provider failures are surfaced without fabricated answers or silent fallback.
4. **Write:** user supplies an essay topic; the Ship 30 skill targets an approximately 1,250-word single-idea essay with a hook, narrative, skimmable headings, actionable takeaway, and citations. The user can regenerate or refine the topic.
5. **Create and view an artifact:** user asks for Markdown or HTML/CSS based on source material; Markdown is rendered safely and HTML is isolated in a sandboxed iframe.
6. **Operate locally:** evaluator can configure `.env`, launch PostgreSQL and the app, migrate, seed, ingest, and troubleshoot dependency readiness.

## Implementation plan

1. Secure local configuration and reproducible startup.
2. Validate migrations, source parsing, repeatable ingestion, and evidence retrieval.
3. Complete provider routing, session APIs, and abstention behavior.
4. Connect Ship 30 and artifact experiences.
5. Verify automated checks and live-stack journeys when Docker/Ollama are available.
