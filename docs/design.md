# Product design

## Principles

- Evidence stays close to the answer: citations show source title, relevance, and a publisher link only when one is known.
- Make system state legible: backend/dependency health, selected model, loading, empty, error, and abstention states are visible.
- Keep common work in one workspace: chat, session history, search, essay drafting, source details, and artifact preview share a consistent shell.
- Keep generated content readable and reviewable; users can inspect citations and switch between an artifact and its source evidence.

## Information architecture

- **Ask Lenny:** conversation thread, suggested starter questions, model selector, composer, citations/evidence panel.
- **Source Search:** ranked indexed chunks, similarity, type, title, available source URL, and source detail API.
- **Ship 30 for 30:** topic input, generation/regeneration, word count, provider status, essay and citations.
- **Documents:** Markdown or HTML/CSS artifact generation and preview.
- **Sidebar:** new chat, recent sessions, active session and main destinations.
- **Status bar:** API readiness, database/model checks, and confirmed provider.

## Interaction states

Empty screens explain what users can do. Loading indicators accompany retrieval or generation. Network and API failures are shown with a clear message. Retry is available by resubmitting the request. The assistant clearly distinguishes evidence insufficiency from provider failure. A missing publisher URL is labeled as a local corpus source rather than shown as a fake link.

## Accessibility and responsive behavior

Use semantic headings, explicit labels, keyboard-operable buttons, `aria-live` for conversation status, and visible focus states. At narrow widths the sidebar and evidence panel should collapse or stack; scrolling remains inside long message and document regions. Maintain readable contrast and avoid relying on color alone for health state.

## Artifact viewer safety

Markdown is translated to React elements, never inserted as raw HTML. HTML uses an iframe with an empty sandbox, restrictive CSP, and no scripts, same-origin access, forms, or network connections. This intentionally prioritizes safe static previews over interactive arbitrary code.
