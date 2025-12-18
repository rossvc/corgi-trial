interface TimestampDisplayProps {
  timestamp: string | null;
  status: 'ok' | 'no_data';
}

export function TimestampDisplay({ timestamp, status }: TimestampDisplayProps) {
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

  const isNoData = status === 'no_data' || !timestamp;

  return (
    <div className={`timestamp-display ${isNoData ? 'no-data' : ''}`}>
      <div className="label">Radar Data</div>
      <div className="time">
        {timestamp ? formatTimestamp(timestamp) : 'Loading...'}
      </div>
    </div>
  );
}
