/**
 * API service module — all network calls to the FastAPI backend.
 *
 * In development the Vite proxy forwards /api/* and /health/* to the backend,
 * so we use relative URLs. In production, set VITE_API_BASE_URL to point at
 * the deployed API.
 *
 * Actual request/response shapes match the backend schemas exactly:
 *   backend/app/schemas/chat.py      → ChatRequest / ChatResponse
 *   backend/app/schemas/retrieval.py → SearchRequest / SearchResponse
 *
 * Never fabricate responses. If the backend is unreachable, let errors
 * propagate so the UI shows a real connection-error message.
 */

// In dev, VITE_API_BASE_URL is "" (empty) so requests go through the proxy.
// In production, set it to e.g. "https://api.yourdomain.com".
const BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  let response;
  try {
    response = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkError) {
    throw new ConnectionError(
      `Cannot reach the backend at ${BASE_URL || window.location.origin}. ` +
        "Make sure the FastAPI server is running.",
      networkError
    );
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = await response.json();
      if (body?.detail) detail = body.detail;
    } catch {
      // ignore JSON parse failure
    }
    throw new ApiError(detail, response.status);
  }

  return response.json();
}

/** Thrown when the server returns a non-2xx status. */
export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/** Thrown when the network request cannot be initiated at all. */
export class ConnectionError extends Error {
  constructor(message, cause) {
    super(message);
    this.name = "ConnectionError";
    this.cause = cause;
  }
}

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

/** GET /health/live */
export async function fetchLiveness() {
  return request("/health/live");
}

/** GET /health/ready — returns { status, checks: { api, database, llm } } */
export async function fetchReadiness() {
  const url = `${BASE_URL}/health/ready`;
  let response;
  try { response = await fetch(url); }
  catch (error) { throw new ConnectionError(`Cannot reach the backend at ${BASE_URL || window.location.origin}. Make sure the FastAPI server is running.`, error); }
  const data = await response.json();
  return data;
}

// ---------------------------------------------------------------------------
// Chat  POST /api/chat
//
// Request:  { question: string, session_id?: string | null, limit?: number }
// Response: { session_id: UUID, answer: string, provider: string,
//              citations: ChatCitation[], abstained: boolean }
// ChatCitation: { source_title, source_url, chunk_id, similarity }
// ---------------------------------------------------------------------------

/**
 * @param {string} question
 * @param {string|null} sessionId   null → start new session
 * @param {number} [limit=5]        1–10
 */
export async function sendChat(question, sessionId = null, limit = 5, provider = null) {
  const body = { question, limit };
  if (sessionId) body.session_id = sessionId;
  if (provider) body.provider = provider;
  return request("/api/chat", { method: "POST", body: JSON.stringify(body) });
}

export async function fetchSessions() { return request("/api/sessions"); }
export async function fetchSession(id) { return request(`/api/sessions/${encodeURIComponent(id)}`); }
export async function fetchProviders() { return request("/api/sessions/providers/options"); }
export async function generateShip30(topic, provider = null, sessionId = null) {
  return request("/api/chat/ship30", { method: "POST", body: JSON.stringify({ topic, provider, session_id: sessionId }) });
}
export async function generateArtifact(prompt, artifactType = "markdown", provider = null, sessionId = null) {
  return request("/api/chat/artifact", { method: "POST", body: JSON.stringify({ prompt, artifact_type: artifactType, provider, session_id: sessionId }) });
}

// ---------------------------------------------------------------------------
// Search  POST /api/search
//
// Request:  { query: string, limit?: number }
// Response: { query: string, results: SearchResult[] }
// SearchResult: { chunk_id, content, chunk_index, source_title,
//                  source_url, source_type, similarity }
// ---------------------------------------------------------------------------

/**
 * @param {string} query
 * @param {number} [limit=5]
 */
export async function searchSources(query, limit = 5) {
  return request("/api/search", {
    method: "POST",
    body: JSON.stringify({ query, limit }),
  });
}
