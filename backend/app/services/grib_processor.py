import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import rasterio
import xarray as xr
from rasterio.crs import CRS
from rasterio.transform import from_bounds

from app.config import DATA_DIR, LATEST_GEOTIFF

logger = logging.getLogger(__name__)


class GRIBProcessor:
    """Processes GRIB2 files and converts them to GeoTIFF."""

    def __init__(self):
        self._last_processed: Optional[Path] = None

    def process_grib(self, grib_path: Path) -> Optional[Path]:
        """
        Process GRIB2 file and convert to GeoTIFF.

        Uses atomic file replacement to prevent partial reads.

        Returns path to the GeoTIFF file, or None on failure.
        """
        if not grib_path.exists():
            logger.error(f"GRIB file not found: {grib_path}")
            return None

        try:
            # Read GRIB2 with xarray/cfgrib
            logger.info(f"Processing {grib_path.name}...")

            ds = xr.open_dataset(
                grib_path,
                engine="cfgrib",
                backend_kwargs={
                    "indexpath": "",  # Disable .idx file creation
                },
            )

            # Extract the data variable (usually 'unknown' for MRMS)
            data_vars = list(ds.data_vars)
            if not data_vars:
                logger.error("No data variables found in GRIB file")
                ds.close()
                return None

            data_var = data_vars[0]
            da = ds[data_var]
            logger.debug(f"Data variable: {data_var}, shape: {da.shape}")

            # Get coordinates
            lats = da.latitude.values
            lons = da.longitude.values

            # MRMS data covers CONUS, typically:
            # Latitude: ~20 to ~55 (north to south in file)
            # Longitude: ~-130 to ~-60 (or 230 to 300 in 0-360 format)

            # Handle longitude wrapping (MRMS uses 0-360 or -180 to 180)
            if lons.max() > 180:
                # Convert from 0-360 to -180 to 180
                lons = np.where(lons > 180, lons - 360, lons)

            # Calculate bounds (west, south, east, north)
            west, east = float(lons.min()), float(lons.max())
            south, north = float(lats.min()), float(lats.max())

            logger.debug(f"Bounds: W={west}, S={south}, E={east}, N={north}")

            # Get data array
            data = da.values.astype(np.float32)

            # Check if latitude is descending (north to south)
            if lats[0] > lats[-1]:
                # Data is already north-up, which is correct for GeoTIFF
                pass
            else:
                # Flip to make north-up
                data = np.flipud(data)
                south, north = north, south

            # Handle no-data values (MRMS uses various values like -999, -99)
            nodata = -999.0
            data = np.where(data < -90, nodata, data)

            # Get dimensions
            height, width = data.shape

            # Create affine transform
            transform = from_bounds(west, south, east, north, width, height)

            # Write to temporary file first (for atomic swap)
            temp_fd, temp_path = tempfile.mkstemp(suffix=".tif", dir=DATA_DIR)
            os.close(temp_fd)
            temp_path = Path(temp_path)

            try:
                with rasterio.open(
                    temp_path,
                    "w",
                    driver="GTiff",
                    height=height,
                    width=width,
                    count=1,
                    dtype=np.float32,
                    crs=CRS.from_epsg(4326),
                    transform=transform,
                    nodata=nodata,
                    compress="deflate",
                ) as dst:
                    dst.write(data, 1)

                # Atomic swap - os.replace is atomic on POSIX
                os.replace(temp_path, LATEST_GEOTIFF)
                logger.info(f"Created GeoTIFF: {LATEST_GEOTIFF.name}")

                self._last_processed = grib_path
                ds.close()

                return LATEST_GEOTIFF

            except Exception as e:
                # Clean up temp file on failure
                if temp_path.exists():
                    temp_path.unlink()
                raise e

        except Exception as e:
            logger.error(f"Failed to process GRIB: {e}")
            return None

    @property
    def last_processed(self) -> Optional[Path]:
        return self._last_processed
