/**
 * ChatInput — text input bar with send button.
 * Handles Enter key (without Shift) and disables input while loading.
 */

import { useState, useRef, useEffect } from "react";
import styles from "./ChatInput.module.css";

export default function ChatInput({ onSend, isLoading, disabled }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = "auto";
    ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
  }, [value]);

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function submit() {
    const trimmed = value.trim();
    if (!trimmed || isLoading || disabled) return;
    onSend(trimmed);
    setValue("");
  }

  return (
    <div className={styles.container}>
      <div className={styles.inputRow}>
        <textarea
          ref={textareaRef}
          id="chat-input"
          className={styles.textarea}
          rows={1}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about Lenny's Podcast or Newsletter…"
          aria-label="Chat message input"
          disabled={isLoading || disabled}
          maxLength={4000}
        />
        <button
          className={`${styles.sendBtn} ${isLoading ? styles.loading : ""}`}
          onClick={submit}
          disabled={!value.trim() || isLoading || disabled}
          aria-label="Send message"
          id="chat-send-btn"
        >
          {isLoading ? (
            <span className={styles.spinner} aria-hidden />
          ) : (
            <svg viewBox="0 0 24 24" className={styles.sendIcon} aria-hidden>
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          )}
        </button>
      </div>
      <p className={styles.hint}>
        Press <kbd>Enter</kbd> to send · <kbd>Shift+Enter</kbd> for new line
      </p>
    </div>
  );
}
