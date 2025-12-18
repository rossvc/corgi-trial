import { MapContainer, TileLayer } from 'react-leaflet';
import { RadarTileLayer } from './RadarTileLayer';
import { ColorLegend } from './ColorLegend';
import { TimestampDisplay } from './TimestampDisplay';
import { useMetadata } from '../hooks/useMetadata';
import 'leaflet/dist/leaflet.css';

export function RadarMap() {
  const { metadata, isLoading, lastUpdated } = useMetadata();

  // Center on CONUS (Continental United States)
  const center: [number, number] = [39.8283, -98.5795];
  const zoom = 5;

  return (
    <div className="radar-map-container">
      <MapContainer
        center={center}
        zoom={zoom}
        maxZoom={14}
        style={{ height: '100%', width: '100%' }}
        zoomControl={true}
      >
        {/* Base map - OpenStreetMap */}
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />

        {/* Radar overlay */}
        <RadarTileLayer timestamp={metadata?.timestamp_unix ?? null} />
      </MapContainer>

      {/* UI Overlays */}
      <TimestampDisplay
        timestamp={metadata?.timestamp ?? null}
        status={metadata?.status ?? 'no_data'}
        isLoading={isLoading}
        lastUpdated={lastUpdated}
      />
      <ColorLegend />
    </div>
  );
}
