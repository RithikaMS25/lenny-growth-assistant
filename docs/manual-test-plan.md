# Manual UI test plan

Run the local stack with the corpus indexed, open `http://127.0.0.1:5173`, and check:

1. Health bar shows actual API/database/model state; unavailable dependencies are not labeled ready.
2. Ask a corpus-supported question; the answer shows title/relevance citations and the evidence panel shows the retrieved text.
3. Ask an unrelated question; the assistant abstains with no fabricated citations.
4. Start another chat, then switch back to the prior saved session; messages and independent history return.
5. Search for a guest or subject; results show ranking and real source metadata. Local records with no URL have no fake external link.
6. Choose Ollama and send a short grounded prompt. Unconfigured cloud providers and experimental Pi are disabled; simulate an unavailable provider and confirm a visible error. If a cloud key is configured, test the Claude Agent SDK path separately.
7. Generate a Ship 30 essay, inspect word count and citations, then regenerate with a revised topic.
8. Generate a Markdown artifact and an HTML/CSS artifact; confirm the Markdown formats and the iframe sandbox has no script or same-origin permission.
9. Navigate with keyboard, use the composer with Enter/Shift+Enter, resize to a narrow viewport, and verify controls remain usable.
