import { useEffect, useRef, useState } from 'react';
import { ComplaintDetail } from 'src/types';

export const usePollingClassify = (shouldPoll: boolean, id: string | undefined) => {
  const [pollingData, setPollingData] = useState<ComplaintDetail | null>(null);
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
        const url = new URL("https://zz0xp1ci31.execute-api.us-east-1.amazonaws.com/dev/getComplaints");
        if (id) url.searchParams.append("complaint_id", id);

        const res = await fetch(url.toString());
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);

        const json: ComplaintDetail = await res.json();
        if (isCancelled) return;

        setPollingData(json);

        const val = json?.complaintClassified;

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