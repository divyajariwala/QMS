import { useEffect, useRef, useState } from "react";
import { API_BASE_URL } from "src/config";

export interface PendingItem {
  id: string;
  text_extracted?: boolean;
}

export interface PollingConfig<TData = any> {
  endpoint: string;
  getPendingItems: (data: TData) => PendingItem[];
  isDone?: (data: TData, pendingItems: PendingItem[]) => boolean;
  headers?: Record<string, string>;
  query?: Record<string, string | number | boolean>;
  pollIntervalMs?: number;
}

const buildUrl = (
  endpoint: string,
  query?: Record<string, string | number | boolean>
) => {
  const isAbsolute = /^https?:\/\//i.test(endpoint);
  const base = isAbsolute ? endpoint : `${API_BASE_URL}${endpoint}`;
  if (!query || Object.keys(query).length === 0) return base;
  const params = new URLSearchParams();
  Object.entries(query).forEach(([k, v]) => params.append(k, String(v)));
  return `${base}${base.includes("?") ? "&" : "?"}${params.toString()}`;
};

export const usePolling = (
  shouldPoll: boolean,
  config: PollingConfig<any> | null,
  maxRetries = 10
) => {
  const [pollingData, setPollingData] = useState<any | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [falseCount, setFalseCount] = useState<number | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const [idList, setIdList] = useState<string[]>([]);

  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const prevFalseCountRef = useRef<number | null>(null);
  const isCancelledRef = useRef(false);

  const pollIntervalMs = config?.pollIntervalMs ?? 10000;

  useEffect(() => {
    if (!config) {
      if (timerRef.current) clearTimeout(timerRef.current);
      setPolling(false);
      return;
    }

    if (!shouldPoll) {
      if (timerRef.current) clearTimeout(timerRef.current);
      setDone(false);
      setError(null);
      setFalseCount(null);
      prevFalseCountRef.current = null;
      setRetryCount(0);
      return;
    }

    if (done) {
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    if (retryCount >= maxRetries) {
      if (timerRef.current) clearTimeout(timerRef.current);
      setError(`Maximum retries of ${maxRetries} reached.`);
      setDone(true);
      return;
    }

    isCancelledRef.current = false;

    const fetchData = async () => {
      setPolling(true);
      setError(null);

      try {
        const url = buildUrl(config.endpoint, config.query);
        const res = await fetch(url, {
          headers: {
            "Content-Type": "application/json",
            ...(config.headers ?? {}),
          },
        });
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const json = await res.json();
        if (isCancelledRef.current) return;

        const pendingItems = config.getPendingItems(json) ?? [];
        const ids = pendingItems.map((p) => p.id).filter(Boolean);

        const currentFalseCount = pendingItems.length;
        setIdList(ids);
        setFalseCount(currentFalseCount);

        const progressed =
          prevFalseCountRef.current === null ||
          prevFalseCountRef.current !== currentFalseCount;

        if (progressed) {
          setPollingData(json);
          prevFalseCountRef.current = currentFalseCount;
          setRetryCount(0); 
        } else {
          setRetryCount((r) => r + 1); 
        }

        const isComplete =
          typeof config.isDone === "function"
            ? config.isDone(json, pendingItems)
            : pendingItems.length === 0;

        if (isComplete) {
          setDone(true);
          if (timerRef.current) clearTimeout(timerRef.current);
          return;
        }
      } catch (err) {
        setError((err as Error).message || "Unknown error");
        setRetryCount((r) => r + 1); 
      } finally {
        if (!isCancelledRef.current) setPolling(false);
      }

      if (!done && !isCancelledRef.current) {
        timerRef.current = setTimeout(fetchData, pollIntervalMs);
      }
    };

    timerRef.current = setTimeout(fetchData, pollIntervalMs);

    return () => {
      isCancelledRef.current = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [shouldPoll, done, maxRetries, retryCount, config, pollIntervalMs]);

  return {
    pollingData,
    polling,
    error,
    done,
    falseCount,
    retryCount,
    idList,
    setIdList,
  };
};
