/**
 * SearchView — raw source search using POST /api/search.
 * Lets users query the vector store directly without invoking the LLM.
 */

import { useState, useCallback } from "react";
import { searchSources, ConnectionError, ApiError } from "../services/api";
import SourcePanel from "./SourcePanel";
import styles from "./SearchView.module.css";

export default function SearchView() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastQuery, setLastQuery] = useState("");

  const handleSearch = useCallback(async () => {
    const q = query.trim();
    if (!q || isLoading) return;
    setError(null);
    setIsLoading(true);
    try {
      const data = await searchSources(q);
      setResults(data.results ?? []);
      setLastQuery(q);
    } catch (err) {
      if (err instanceof ConnectionError) {
        setError(`Cannot reach backend: ${err.message}`);
      } else if (err instanceof ApiError) {
        setError(`Error ${err.status}: ${err.message}`);
      } else {
        setError(String(err));
      }
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [query, isLoading]);

  function handleKeyDown(e) {
    if (e.key === "Enter") handleSearch();
  }

  return (
    <div className={styles.view}>
      <div className={styles.searchArea}>
        <h1 className={styles.title}>Source Search</h1>
        <p className={styles.subtitle}>
          Query the vector store directly — bypasses the LLM and returns raw
          chunks ranked by cosine similarity.
        </p>

        <div className={styles.inputRow}>
          <input
            id="search-input"
            type="text"
            className={styles.input}
            placeholder="Search Lenny's transcripts…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            aria-label="Search query"
            disabled={isLoading}
          />
          <button
            id="search-btn"
            className={styles.btn}
            onClick={handleSearch}
            disabled={!query.trim() || isLoading}
            aria-label="Run search"
          >
            {isLoading ? <span className={styles.spinner} aria-hidden /> : "Search"}
          </button>
        </div>

        {error && (
          <div className={styles.error} role="alert">{error}</div>
        )}

        {lastQuery && !isLoading && (
          <p className={styles.resultMeta}>
            {results.length} result{results.length !== 1 ? "s" : ""} for <em>"{lastQuery}"</em>
          </p>
        )}
      </div>

      <SourcePanel results={results} isLoading={isLoading} error={null} />
    </div>
  );
}
