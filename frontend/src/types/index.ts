export interface RadarMetadata {
  timestamp: string | null;
  timestamp_unix: number | null;
  status: 'ok' | 'no_data';
  message?: string;
  bounds: {
    west: number;
    south: number;
    east: number;
    north: number;
  };
}
