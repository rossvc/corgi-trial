import { RadarMetadata } from '../types';

const API_BASE = '';  // Using Vite proxy

export async function fetchMetadata(): Promise<RadarMetadata> {
  const response = await fetch(`${API_BASE}/api/metadata`);

  if (!response.ok) {
    throw new Error(`Failed to fetch metadata: ${response.status}`);
  }

  return response.json();
}

export function getTileUrl(timestamp: number | null): string {
  const base = `${API_BASE}/tiles/{z}/{x}/{y}.png`;

  if (timestamp) {
    return `${base}?t=${timestamp}`;
  }

  return base;
}
