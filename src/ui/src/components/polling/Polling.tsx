import { useEffect, useRef, useState } from 'react';
import { getComplaintsApiResponse } from 'src/types';

export const usePolling = (shouldPoll: boolean) => {
  const [pollingData, setPollingData] = useState<getComplaintsApiResponse | null>(null);
  const [polling, setPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!shouldPoll) {
      // Stop polling and reset done if polling turned off externally
      if (timerRef.current) clearTimeout(timerRef.current);
      setDone(false);
      return;
    }
    if (done) {
      // Stop polling when done = true
      if (timerRef.current) clearTimeout(timerRef.current);
      return;
    }

    let isCancelled = false;

    const fetchData = async () => {
      setPolling(true);
      setError(null);
      try {
        const res = await fetch(
          'https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/getComplaints?status=pending&page=1'
        );
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const json: getComplaintsApiResponse = await res.json();
        if (isCancelled) return;

        setPollingData(json);

        const val = json?.caseStatus?.pending?.[0]?.text_extracted;

        if (val) {
          setDone(true);
          if (timerRef.current) clearTimeout(timerRef.current);
          return;
        }
      } catch (err) {
        setError((err as Error).message || 'Unknown error');
      } finally {
        setPolling(false);
      }

      if (!done && !isCancelled) {
        timerRef.current = setTimeout(fetchData, 10000);
      }
    };

    // Run immediately
    fetchData();

    return () => {
      isCancelled = true;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [shouldPoll, done]);

  return { pollingData, polling, error, done };
};