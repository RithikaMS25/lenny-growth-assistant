/**
 * useHealthCheck — polls /health/ready on mount and after errors.
 * Exposes the backend status so the UI can warn the user accurately.
 */

import { useState, useEffect } from "react";
import { fetchReadiness, ConnectionError } from "../services/api";

export function useHealthCheck() {
  const [health, setHealth] = useState({
    status: "checking", // "checking" | "ok" | "not_ready" | "unreachable"
    checks: {},
  });

  useEffect(() => {
    let cancelled = false;

    async function check() {
      try {
        const data = await fetchReadiness();
        if (!cancelled)
          setHealth({ status: data.status, checks: data.checks ?? {} });
      } catch (err) {
        if (!cancelled) {
          if (err instanceof ConnectionError) {
            setHealth({ status: "unreachable", checks: {} });
          } else {
            setHealth({ status: "not_ready", checks: {} });
          }
        }
      }
    }

    check();
    return () => {
      cancelled = true;
    };
  }, []);

  return health;
}
