import asyncio
import aiohttp
import gzip
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from email.utils import parsedate_to_datetime

from app.config import (
    NOAA_BASE_URL,
    NOAA_LATEST_FILE,
    DATA_DIR,
    POLL_INTERVAL,
    MAX_GRIB_FILES,
)

logger = logging.getLogger(__name__)


class MRMSFetcher:
    """Fetches MRMS radar data from NOAA."""

    def __init__(self):
        self.current_file: Optional[Path] = None
        self.current_timestamp: Optional[datetime] = None
        self.last_modified: Optional[str] = None
        self._running = False
        self._backoff = POLL_INTERVAL

    @property
    def url(self) -> str:
        return f"{NOAA_BASE_URL}{NOAA_LATEST_FILE}"

    async def start_polling(self):
        """Background task that polls NOAA for new data."""
        self._running = True
        logger.info(f"Starting MRMS fetcher, polling every {POLL_INTERVAL}s")

        # Fetch immediately on startup
        await self._fetch_latest()

        while self._running:
            await asyncio.sleep(self._backoff)
            try:
                await self._fetch_latest()
                self._backoff = POLL_INTERVAL  # Reset backoff on success
            except Exception as e:
                logger.error(f"Fetch error: {e}")
                # Exponential backoff, max 10 minutes
                self._backoff = min(self._backoff * 2, 600)
                logger.info(f"Backing off to {self._backoff}s")

    def stop(self):
        """Stop the polling loop."""
        self._running = False

    async def _fetch_latest(self):
        """Download and decompress the latest GRIB2 file if it's new."""
        timeout = aiohttp.ClientTimeout(total=60)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Check Last-Modified header first
            try:
                async with session.head(self.url) as resp:
                    if resp.status != 200:
                        logger.warning(f"HEAD request failed: {resp.status}")
                        return

                    last_modified = resp.headers.get("Last-Modified")
                    if last_modified == self.last_modified:
                        logger.debug("No new data available")
                        return
            except Exception as e:
                logger.warning(f"HEAD request failed: {e}, proceeding with GET")

            # Download the file
            logger.info("Fetching new radar data...")
            async with session.get(self.url) as resp:
                if resp.status != 200:
                    logger.error(f"GET request failed: {resp.status}")
                    return

                compressed = await resp.read()
                self.last_modified = resp.headers.get("Last-Modified")

                # Parse timestamp from Last-Modified or use current time
                try:
                    if self.last_modified:
                        timestamp = parsedate_to_datetime(self.last_modified)
                    else:
                        timestamp = datetime.utcnow()
                except Exception:
                    timestamp = datetime.utcnow()

                # Decompress
                try:
                    decompressed = gzip.decompress(compressed)
                except gzip.BadGzipFile as e:
                    logger.error(f"Failed to decompress: {e}")
                    return

                # Save with timestamp in filename
                filename = f"reflectivity_{timestamp.strftime('%Y%m%d_%H%M%S')}.grib2"
                filepath = DATA_DIR / filename

                filepath.write_bytes(decompressed)
                logger.info(f"Saved {filepath.name} ({len(decompressed) / 1024 / 1024:.1f} MB)")

                self.current_file = filepath
                self.current_timestamp = timestamp

                # Clean up old files
                self._cleanup_old_files()

    def _cleanup_old_files(self):
        """Keep only the last N GRIB2 files."""
        grib_files = sorted(DATA_DIR.glob("reflectivity_*.grib2"), reverse=True)

        for old_file in grib_files[MAX_GRIB_FILES:]:
            try:
                old_file.unlink()
                logger.debug(f"Deleted old file: {old_file.name}")
            except Exception as e:
                logger.warning(f"Failed to delete {old_file.name}: {e}")
