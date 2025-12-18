interface RefreshIndicatorProps {
  isLoading: boolean;
  lastUpdated: Date | null;
}

export function RefreshIndicator({
  isLoading,
  lastUpdated,
}: RefreshIndicatorProps) {
  const formatLastUpdate = (date: Date): string => {
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);

    if (seconds < 60) {
      return `${seconds}s ago`;
    }

    const minutes = Math.floor(seconds / 60);
    return `${minutes}m ago`;
  };

  return (
    <div className="refresh-indicator">
      {isLoading && <div className="spinner" />}
      <div className={`status ${isLoading ? 'loading' : ''}`}>
        {isLoading ? 'Checking for updates...' : 'Live'}
      </div>
      {lastUpdated && !isLoading && (
        <div className="last-update">
          Updated {formatLastUpdate(lastUpdated)}
        </div>
      )}
    </div>
  );
}
