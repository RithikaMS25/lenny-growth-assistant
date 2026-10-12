/**
 * StatusBar — shows backend health and active provider.
 * Only shows the provider name when the backend has confirmed it.
 */

import { useHealthCheck } from "../hooks/useHealthCheck";
import styles from "./StatusBar.module.css";

const STATUS_CONFIG = {
  checking:   { label: "Connecting…",   dot: "yellow",  },
  ok:         { label: "Backend ready", dot: "green",   },
  not_ready:  { label: "Backend not ready", dot: "red", },
  unreachable:{ label: "Backend unreachable", dot: "red",},
};

export default function StatusBar({ provider }) {
  const health = useHealthCheck();
  const config = STATUS_CONFIG[health.status] ?? STATUS_CONFIG.checking;

  return (
    <div className={styles.bar} role="status" aria-live="polite">
      <span className={`${styles.dot} ${styles[config.dot]}`} />
      <span className={styles.label}>{config.label}</span>

      {health.checks?.database && (
        <span className={styles.chip}>
          DB: {health.checks.database}
        </span>
      )}
      {health.checks?.llm && <span className={styles.chip}>Model health: {health.checks.llm}</span>}

      {/* Provider is only rendered when the backend explicitly returns it */}
      {provider && (
        <span className={`${styles.chip} ${styles.provider}`}>
          Model: {provider}
        </span>
      )}
    </div>
  );
}
