/**
 * useChatSession — manages a single chat conversation.
 *
 * session_id returned by the backend is preserved and reused for every
 * follow-up message, exactly as required by ChatRequest.session_id.
 */

import { useState, useCallback } from "react";
import { sendChat, ConnectionError, ApiError, fetchSession } from "../services/api";

export function useChatSession() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError]     = useState(null);   // { type, message }
  const [provider, setProvider] = useState(null);  // confirmed by backend
  const [selectedProvider, setSelectedProvider] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  const appendMessage = useCallback((msg) => {
    setMessages((prev) => [...prev, { ...msg, id: crypto.randomUUID() }]);
  }, []);

  const sendMessage = useCallback(
    async (question) => {
      if (!question.trim() || isLoading) return;

      setError(null);
      appendMessage({ role: "user", content: question.trim() });
      setIsLoading(true);

      try {
        const response = await sendChat(question.trim(), sessionId, 5, selectedProvider);

        // Persist session_id for follow-up messages.
        setSessionId(response.session_id);

        // Record the provider exactly as returned by the backend.
        setProvider(response.provider ?? null);

        appendMessage({
          role:      "assistant",
          content:   response.answer,
          citations: response.citations ?? [],
          provider:  response.provider,
          abstained: response.abstained,
        });
      } catch (err) {
        if (err instanceof ConnectionError) {
          setError({ type: "connection", message: err.message });
        } else if (err instanceof ApiError) {
          setError({
            type: "api",
            message: `Server error (${err.status}): ${err.message}`,
          });
        } else {
          setError({ type: "unknown", message: String(err) });
        }
      } finally {
        setIsLoading(false);
      }
    },
    [isLoading, appendMessage, selectedProvider, sessionId]
  );

  const loadSession = useCallback(async (id) => {
    setError(null); setIsLoading(true);
    try {
      const data = await fetchSession(id);
      setSessionId(data.id);
      setMessages(data.messages.map((m) => ({ ...m, id: m.id })));
      setProvider([...data.messages].reverse().find((m) => m.provider)?.provider ?? null);
    } catch (err) { setError({ type: "api", message: err.message }); }
    finally { setIsLoading(false); }
  }, []);

  return {
    messages,
    isLoading,
    error,
    provider,
    selectedProvider, setSelectedProvider,
    sessionId,
    sendMessage,
    loadSession,
  };
}
