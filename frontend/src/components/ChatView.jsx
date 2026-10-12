/**
 * ChatView — the main chat interface.
 *
 * Combines: message thread, loading indicator, error banner, input bar,
 * and triggers source panel updates via onSourcesUpdate callback.
 */

import { useEffect, useRef } from "react";
import { useChatSession } from "../hooks/useChatSession";
import ChatMessage from "./ChatMessage";
import ChatInput from "./ChatInput";
import styles from "./ChatView.module.css";

export default function ChatView({ onSessionChange, onProviderChange, onSelectedProviderChange, onSourcesUpdate, onSessionListChange, onSelectSession, onProviderOptions, defaultProvider }) {
  const { messages, isLoading, error, sessionId, provider, selectedProvider, setSelectedProvider, sendMessage, loadSession } =
    useChatSession();
  useEffect(() => { onSelectSession?.(loadSession); }, [loadSession, onSelectSession]);
  useEffect(() => { if (sessionId) onSessionListChange?.(); }, [sessionId, onSessionListChange]);
  useEffect(() => { if (!selectedProvider && defaultProvider) setSelectedProvider(defaultProvider); }, [selectedProvider, defaultProvider, setSelectedProvider]);
  useEffect(() => { onSelectedProviderChange?.(selectedProvider || defaultProvider); }, [selectedProvider, defaultProvider, onSelectedProviderChange]);
  const bottomRef = useRef(null);

  // Notify parent of session ID changes (for sidebar display).
  useEffect(() => {
    onSessionChange?.(sessionId);
  }, [sessionId, onSessionChange]);

  // Notify parent of confirmed provider name for the StatusBar.
  useEffect(() => {
    onProviderChange?.(provider);
  }, [provider, onProviderChange]);

  // Scroll to the bottom after each new message.
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // When the last assistant message arrives, push its citations to the
  // SourcePanel so the evidence panel shows what the LLM actually used.
  useEffect(() => {
    const lastAssistant = [...messages]
      .reverse()
      .find((m) => m.role === "assistant");
    if (lastAssistant?.citations?.length) {
      // Convert ChatCitation to SearchResult shape for SourcePanel.
      const adapted = lastAssistant.citations.map((c) => ({
        chunk_id: c.chunk_id,
        content: c.content ?? "",
        chunk_index: 0,
        source_title: c.source_title,
        source_url: c.source_url,
        source_type: "citation",
        similarity: c.similarity,
      }));
      onSourcesUpdate?.(adapted);
    }
  }, [messages, onSourcesUpdate]);

  const isEmpty = messages.length === 0;

  return (
    <div className={styles.view}>
      {/* Message thread */}
      <div className={styles.thread} role="log" aria-live="polite" aria-label="Chat messages">
        {isEmpty && !isLoading && (
          <div className={styles.empty}>
            <div className={styles.emptyIcon}>💬</div>
            <h1 className={styles.emptyTitle}>Ask Lenny anything</h1>
            <p className={styles.emptySubtitle}>
              Questions are answered using real content from Lenny&apos;s Podcast
              and Newsletter. The assistant will cite its sources and tell you
              when evidence is insufficient.
            </p>
            <div className={styles.suggestions}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className={styles.suggestion}
                  onClick={() => sendMessage(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <ChatMessage key={msg.id} message={msg} />
        ))}

        {/* Typing indicator */}
        {isLoading && (
          <div className={styles.typingWrapper} role="status" aria-label="Assistant is thinking">
            <div className={styles.avatar} aria-hidden>L</div>
            <div className={styles.typing}>
              <span /><span /><span />
            </div>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className={styles.errorBanner} role="alert">
            <strong>
              {error.type === "connection" ? "⚡ Connection error" : "⚠️ Error"}
            </strong>{" "}
            — {error.message}
            {error.type === "connection" && (
              <span className={styles.errorHint}>
                {" "}Start the FastAPI backend and reload.
              </span>
            )}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className={styles.composerHead}><label htmlFor="provider-select">Model</label><select id="provider-select" value={selectedProvider ?? ""} onChange={(e) => setSelectedProvider(e.target.value || null)}>{(onProviderOptions ?? []).map((p) => <option key={p.id} value={p.id} disabled={!p.available}>{p.id}{p.available ? ` · ${p.model}` : " · key not configured"}</option>)}</select></div>
      <ChatInput onSend={sendMessage} isLoading={isLoading} />
    </div>
  );
}

const SUGGESTIONS = [
  "What are the best strategies for early user retention?",
  "What does Lenny say about finding product-market fit?",
  "How should a PM think about metrics for a new product?",
];
