import { useState, useEffect } from 'react';

interface TimestampDisplayProps {
  timestamp: string | null;
  status: 'ok' | 'no_data';
  isLoading: boolean;
  lastUpdated: Date | null;
}

export function TimestampDisplay({ timestamp, status, isLoading, lastUpdated }: TimestampDisplayProps) {
  // Force re-render every second to update elapsed time display
  const [, setTick] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 1000);
    return () => clearInterval(interval);
  }, []);

  const formatTimestamp = (iso: string): string => {
    const date = new Date(iso);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZoneName: 'short',
    });
  };

  const formatLastUpdate = (date: Date): string => {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    if (seconds < 60) {
      return `${seconds}s ago`;
    }
    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ago`;
  };

  const isNoData = status === 'no_data' || !timestamp;

  return (
    <div className={`timestamp-display ${isNoData ? 'no-data' : ''}`}>
      <div className="label">Radar Data</div>
      <div className="time-row">
        <span className="time">
          {timestamp ? formatTimestamp(timestamp) : 'Loading...'}
        </span>
        {isLoading ? (
          <>
            <span className="separator">·</span>
            <div className="spinner" />
          </>
        ) : lastUpdated ? (
          <>
            <span className="separator">·</span>
            <span className="last-update">{formatLastUpdate(lastUpdated)}</span>
          </>
        ) : null}
      </div>
    </div>
  );
}
