import { useEffect, useRef, useState } from 'react';
import { getComplaintsApiResponse } from 'src/types';

export const usePolling = (shouldPoll: boolean, maxRetries = 10) => {
  const [pollingData, setPollingData] = useState<getComplaintsApiResponse | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const [falseCount, setFalseCount] = useState<number | null>(null);
  const [retryCount, setRetryCount] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const prevFalseCountRef = useRef<number | null>(null);
  const isCancelledRef = useRef(false);

  useEffect(() => {
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
        const res = await fetch(
          'https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/getComplaints?status=pending&page=1'
        );
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const json: getComplaintsApiResponse = await res.json();
        if (isCancelledRef.current) return;

        const currentFalseCount = json?.caseStatus?.pending?.filter(e => e?.text_extracted === false).length ?? 0;
        setFalseCount(currentFalseCount);

        if (prevFalseCountRef.current === null || prevFalseCountRef.current !== currentFalseCount) {
          setPollingData(json);
          prevFalseCountRef.current = currentFalseCount;
          setRetryCount(0); // reset retries on progress
        } else {
          setRetryCount(r => r + 1); // increment retry if no progress
        }

        if (currentFalseCount === 0) {
          setDone(true);
          if (timerRef.current) clearTimeout(timerRef.current);
          return;
        }
      } catch (err) {
        setError((err as Error).message || 'Unknown error');
        setRetryCount(r => r + 1); // increment retry on error too
      } finally {
        if (!isCancelledRef.current) setPolling(false);
      }

      if (!done && !isCancelledRef.current) {
        timerRef.current = setTimeout(fetchData, 10000);
      }
    };

    // Schedule the first fetch after 10 seconds instead of calling immediately
    timerRef.current = setTimeout(fetchData, 10000);

    return () => {
      isCancelledRef.current = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [shouldPoll, done, maxRetries, retryCount]);

  return { pollingData, polling, error, done, falseCount, retryCount };
};