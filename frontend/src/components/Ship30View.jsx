/**
 * Ship30View — UI structure for the Ship 30 for 30 essay-writing feature.
 *
 * NOTE: The backend does NOT yet expose a Ship 30 endpoint.
 * This component provides the full UI structure but clearly communicates
 * that the feature is not yet available. No fake API calls are made.
 */

import { useState } from "react";
import { generateShip30 } from "../services/api";
import SafeMarkdown from "./SafeMarkdown";
import styles from "./Ship30View.module.css";

export default function Ship30View({ provider = null, sessionId = null, onArtifact, onOpenArtifact }) {
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function generate() {
    setBusy(true); setError("");
    try { const data = await generateShip30(topic, provider, sessionId); setResult(data); onArtifact?.({type:"markdown", content:data.essay, citations:data.citations}); }
    catch (err) { setError(err.message); }
    finally { setBusy(false); }
  }
  return (
    <div className={styles.view}>
      <div className={styles.header}>
        <div className={styles.badge}>Evidence grounded</div>
        <h1 className={styles.title}>Ship 30 for 30</h1>
        <p className={styles.subtitle}>
          Develop an approximately 1,250-word essay from relevant podcast and newsletter evidence.
        </p>

      </div>

      {/* Essay generator scaffold */}
      <div className={styles.generator}>
        <div className={styles.col}>
          <label className={styles.fieldLabel} htmlFor="essay-topic">
            Essay topic
          </label>
          <textarea
            id="essay-topic"
            className={styles.topicInput}
            rows={4} value={topic} onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g. How to find product-market fit for a B2B SaaS product"
          />

          <label className={styles.fieldLabel} htmlFor="essay-format">
            Format
          </label>
          <select
            id="essay-format"
            className={styles.select}
            disabled
          >
            <option>Ship 30 essay · approximately 1,250 words</option>
          </select>

          <button
            id="essay-generate-btn"
            className={styles.generateBtn}
            disabled={busy || topic.trim().length < 8} onClick={generate}
          >
            {busy ? "Writing…" : result ? "Regenerate essay" : "Generate essay"}
          </button>

          {error && <p role="alert" className={styles.disabledHint}>{error}</p>}
          {result?.abstained && <p role="status" className={styles.disabledHint}>{result.essay}</p>}
        </div>

        <div className={styles.col}>
          <label className={styles.fieldLabel}>
            Generated essay
          </label>
          <div className={styles.outputArea} role="region" aria-label="Generated essay output" style={{display:"block",overflow:"auto"}}>
            {result ? <><p>{result.word_count} words · {result.provider}{result.abstained ? " · evidence insufficient" : ""}</p><SafeMarkdown source={result.essay} />{result.citations.length > 0 && <><h3>Sources</h3>{result.citations.map((c)=><p key={c.chunk_id}>{c.source_url ? <a href={c.source_url} target="_blank" rel="noreferrer">{c.source_title}</a> : c.source_title}</p>)}</>}{!result.abstained && <button onClick={()=>onOpenArtifact?.({type:"markdown",content:result.essay,citations:result.citations})}>Open beside chat</button>}</> : <span className={styles.outputPlaceholder}>Your generated essay will appear here.</span>}
          </div>
        </div>
      </div>
    </div>
  );
}
