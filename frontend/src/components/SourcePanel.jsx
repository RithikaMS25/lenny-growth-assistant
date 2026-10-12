/**
 * SourcePanel — displays retrieved evidence chunks from the search API
 * or from the citations returned by the chat API.
 *
 * Each source card shows the real data returned by the backend.
 * External links open in a new tab with rel="noopener noreferrer".
 */

import styles from "./SourcePanel.module.css";

function SourceCard({ result }) {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <span className={styles.sourceType}>{result.source_type}</span>
        <span
          className={styles.similarity}
          title="Cosine similarity to your query"
        >
          {(result.similarity * 100).toFixed(1)}%
        </span>
      </div>

      <p className={styles.cardTitle}>{result.source_title}</p>

      <p className={styles.cardContent}>{result.content}</p>

      <div className={styles.cardFooter}>
        {result.source_url ? <a href={result.source_url} target="_blank" rel="noopener noreferrer" className={styles.sourceLink} aria-label={`Open source: ${result.source_title}`}>Open source ↗</a> : <span className={styles.sourceLink}>Local corpus source</span>}
        <span className={styles.chunkIndex}>chunk #{result.chunk_index}</span>
      </div>
    </div>
  );
}

export default function SourcePanel({ results, isLoading, error, artifactOpen = false, hasArtifact = false, onShowEvidence, onShowArtifact }) {
  return (
    <aside className={styles.panel} aria-label="Retrieved sources">
      <div className={styles.panelHeader}>
        <h2 className={styles.panelTitle}>Evidence</h2>
        <div><button type="button" onClick={onShowEvidence} aria-pressed={!artifactOpen}>Evidence</button><button type="button" onClick={onShowArtifact} disabled={!hasArtifact} aria-pressed={artifactOpen}>Artifact</button></div>
        {results.length > 0 && (
          <span className={styles.count}>{results.length} chunk{results.length !== 1 ? "s" : ""}</span>
        )}
      </div>

      {isLoading && (
        <div className={styles.loading} role="status">
          <span className={styles.loadingSpinner} aria-hidden />
          Retrieving sources…
        </div>
      )}

      {error && (
        <div className={styles.error} role="alert">
          {error}
        </div>
      )}

      {!isLoading && !error && results.length === 0 && (
        <div className={styles.empty}>
          <span className={styles.emptyIcon}>📚</span>
          <p>Retrieved sources will appear here after you ask a question.</p>
        </div>
      )}

      <div className={styles.cards}>
        {results.map((r) => (
          <SourceCard key={r.chunk_id} result={r} />
        ))}
      </div>
    </aside>
  );
}
