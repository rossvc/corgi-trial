import { useState, useEffect, useCallback } from 'react';
import { fetchMetadata } from '../services/api';
import { RadarMetadata } from '../types';

const POLL_INTERVAL = 60000; // 60 seconds

export function useMetadata() {
  const [metadata, setMetadata] = useState<RadarMetadata | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await fetchMetadata();
      setMetadata(data);
      setLastUpdated(new Date());
      setError(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to fetch radar data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    refresh();
  }, [refresh]);

  // Polling
  useEffect(() => {
    const interval = setInterval(refresh, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [refresh]);

  return { metadata, isLoading, lastUpdated, error, refresh };
}
