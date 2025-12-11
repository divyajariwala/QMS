import { useEffect, useRef, useState } from 'react';
import { API_BASE_URL } from 'src/config';
import { ComplaintDetail } from 'src/types';

export const usePollingClassify = (shouldPoll: boolean, id: string | undefined, maxRetries = 5) => {
  const [pollingData, setPollingData] = useState<ComplaintDetail | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const retryCountRef = useRef(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const isCancelledRef = useRef(false);

  // To track if complaint classified status changed, 
  // so that retry count resets on progress
  const prevClassifiedRef = useRef<boolean | null>(null);

  useEffect(() => {
    if (!shouldPoll) {
      if (timerRef.current) clearTimeout(timerRef.current);
      setDone(false);
      setError(null);
      retryCountRef.current = 0;
      prevClassifiedRef.current = null;
      return;
    }

    if (done) {
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    if (retryCountRef.current >= maxRetries) {
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
        const url = new URL(`${API_BASE_URL}dev/getComplaints`);
        if (id) url.searchParams.append("complaint_id", id);

        const res = await fetch(url.toString());
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const json: ComplaintDetail = await res.json();
        if (isCancelledRef.current) return;

        setPollingData(json);

        const currentClassified = !!json?.complaintClassified;

        // Reset retryCount on progress
        if (prevClassifiedRef.current === null || prevClassifiedRef.current !== currentClassified) {
          retryCountRef.current = 0; 
          prevClassifiedRef.current = currentClassified;
        } else {
          // No progress, increment retryCount
          retryCountRef.current += 1;
        }

        if (currentClassified) {
          setDone(true);
          if (timerRef.current) clearTimeout(timerRef.current);
          retryCountRef.current = 0;
          return;
        }
      } catch (err) {
        setError((err as Error).message || 'Unknown error');
        retryCountRef.current += 1; // increment retry on error too
      } finally {
        if (!isCancelledRef.current) setPolling(false);
      }

      if (!done && !isCancelledRef.current && retryCountRef.current < maxRetries) {
        if (timerRef.current) clearTimeout(timerRef.current);
        timerRef.current = setTimeout(fetchData, 10000);
      } else if (retryCountRef.current >= maxRetries) {
        setError(`Maximum retries of ${maxRetries} reached.`);
        setDone(true);
        retryCountRef.current = 0;
      }
    };

    // Start first fetch after 10 seconds delay (feel free to change)
    timerRef.current = setTimeout(fetchData, 10000);

    return () => {
      isCancelledRef.current = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [shouldPoll, id, done, maxRetries]);

  return { pollingData, polling, error, done };
};