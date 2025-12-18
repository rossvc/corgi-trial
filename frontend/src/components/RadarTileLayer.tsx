import { TileLayer } from 'react-leaflet';
import { getTileUrl } from '../services/api';

interface RadarTileLayerProps {
  timestamp: number | null;
}

export function RadarTileLayer({ timestamp }: RadarTileLayerProps) {
  const tileUrl = getTileUrl(timestamp);

  // Using key={timestamp} forces React to unmount and remount the TileLayer
  // when timestamp changes. This clears Leaflet's internal tile cache and
  // forces fresh tile requests. The ?t= parameter also busts browser cache.
  //
  // Note: This causes a brief blink (~200-500ms) during refresh.
  // For a smoother experience, could implement double-buffered layers.

  return (
    <TileLayer
      key={timestamp ?? 'no-data'}
      url={tileUrl}
      opacity={0.7}
      zIndex={1000}
    />
  );
}
