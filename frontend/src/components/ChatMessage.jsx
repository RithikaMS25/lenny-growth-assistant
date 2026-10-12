/**
 * ChatMessage — renders a single user or assistant message bubble.
 * - Displays abstention state with a distinct visual treatment.
 * - Does NOT dangerously render arbitrary HTML from the backend.
 */

import styles from "./ChatMessage.module.css";
import SafeMarkdown from "./SafeMarkdown";

export default function ChatMessage({ message }) {
  const isUser = message.role === "user";
  const isAbstained = !isUser && message.abstained;

  return (
    <article
      className={`${styles.wrapper} ${isUser ? styles.user : styles.assistant}`}
      aria-label={`${message.role} message`}
    >
      <div className={styles.avatar} aria-hidden>
        {isUser ? "You" : "L"}
      </div>

      <div className={styles.bubble}>
        {/* Content — rendered as plain text, no innerHTML */}
        <div className={`${styles.text} ${isAbstained ? styles.abstained : ""}`}><SafeMarkdown source={message.content} /></div>

        {/* Citations */}
        {!isUser && message.citations?.length > 0 && (
          <div className={styles.citations}>
            <span className={styles.citationsLabel}>Sources</span>
            {message.citations.map((c) => (
              c.source_url ? <a
                key={c.chunk_id}
                href={c.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.citation}
                title={`Similarity: ${(c.similarity * 100).toFixed(1)}%`}
              >
                <span className={styles.citationTitle}>{c.source_title}</span>
                <span className={styles.citationScore}>
                  {(c.similarity * 100).toFixed(0)}%
                </span>
              </a> : <span key={c.chunk_id} className={styles.citation}><span className={styles.citationTitle}>{c.source_title}</span><span className={styles.citationScore}>{(c.similarity * 100).toFixed(0)}%</span></span>
            ))}
          </div>
        )}

        {/* Abstention notice */}
        {isAbstained && (
          <div className={styles.abstainedNotice} role="note">
            ⚠️ Insufficient evidence — the assistant did not generate an answer.
          </div>
        )}
      </div>
    </article>
  );
}
