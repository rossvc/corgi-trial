import io
import logging
from typing import Optional

import numpy as np
from PIL import Image
from rio_tiler.io import Reader
from rio_tiler.errors import TileOutsideBounds

from app.config import LATEST_GEOTIFF

logger = logging.getLogger(__name__)

# NOAA Standard Radar Color Ramp (discrete/banded)
# Each entry is (min_dbz, max_dbz): (R, G, B, A)
RADAR_BANDS = [
    # Below threshold - transparent
    (-999, 5, (0, 0, 0, 0)),
    (5, 10, (0, 0, 0, 0)),
    # Light precipitation (blues)
    (10, 15, (64, 164, 176, 200)),    # Teal
    (15, 20, (64, 128, 255, 220)),    # Light blue
    # Light rain (cyans/greens)
    (20, 25, (0, 236, 236, 230)),     # Cyan
    (25, 30, (0, 192, 0, 240)),       # Light green
    # Moderate (greens)
    (30, 35, (0, 144, 0, 250)),       # Green
    (35, 40, (0, 100, 0, 255)),       # Dark green
    # Moderate-heavy (yellows)
    (40, 45, (255, 255, 0, 255)),     # Yellow
    (45, 50, (255, 192, 0, 255)),     # Orange-yellow
    # Heavy (oranges/reds)
    (50, 55, (255, 128, 0, 255)),     # Orange
    (55, 60, (255, 0, 0, 255)),       # Red
    # Very heavy (dark reds)
    (60, 65, (192, 0, 0, 255)),       # Dark red
    (65, 70, (144, 0, 0, 255)),       # Darker red
    # Severe (magentas/purples)
    (70, 75, (255, 0, 255, 255)),     # Magenta
    (75, 80, (192, 0, 192, 255)),     # Purple
    (80, 999, (128, 64, 255, 255)),   # Violet (extreme)
]


def build_discrete_colormap() -> dict:
    """
    Build a 256-entry colormap for rio-tiler.

    Maps scaled pixel values (0-255) back to dBZ and assigns discrete colors.
    The colormap uses intervals/bands, not linear interpolation.
    """
    colormap = {}

    # rio-tiler rescales data to 0-255
    # We need to map these back to dBZ values
    # Assuming data range: -10 to 80 dBZ (90 dBZ range)
    dbz_min = -10
    dbz_max = 80
    dbz_range = dbz_max - dbz_min

    for i in range(256):
        # Convert pixel value back to dBZ
        dbz = dbz_min + (i / 255.0) * dbz_range

        # Find the appropriate color band (discrete, not interpolated)
        color = (0, 0, 0, 0)  # Default transparent
        for min_dbz, max_dbz, band_color in RADAR_BANDS:
            if min_dbz <= dbz < max_dbz:
                color = band_color
                break

        colormap[i] = color

    return colormap


# Pre-build the colormap for performance
DISCRETE_COLORMAP = build_discrete_colormap()


class TileRenderer:
    """Renders XYZ map tiles from GeoTIFF radar data."""

    def __init__(self):
        self._empty_tile: Optional[bytes] = None

    def get_tile(self, z: int, x: int, y: int) -> bytes:
        """
        Generate a PNG tile for the given z/x/y coordinates.

        Uses Web Mercator (EPSG:3857) tile scheme.
        Returns transparent tile if data unavailable or out of bounds.
        """
        if not LATEST_GEOTIFF.exists():
            return self._get_empty_tile()

        try:
            with Reader(str(LATEST_GEOTIFF)) as src:
                # rio-tiler handles EPSG:4326 -> EPSG:3857 reprojection
                img = src.tile(x, y, z, tilesize=256)

                # Rescale dBZ values to 0-255 for colormap
                # MRMS reflectivity typically -10 to 80 dBZ
                img.rescale(
                    in_range=((-10, 80),),
                    out_range=((0, 255),),
                )

                # Apply discrete colormap and render to PNG
                content = img.render(
                    colormap=DISCRETE_COLORMAP,
                    img_format="PNG",
                )

                return content

        except TileOutsideBounds:
            # Tile is outside the data extent
            return self._get_empty_tile()
        except Exception as e:
            logger.warning(f"Tile error z={z} x={x} y={y}: {e}")
            return self._get_empty_tile()

    def _get_empty_tile(self) -> bytes:
        """Return a cached transparent 256x256 PNG tile."""
        if self._empty_tile is None:
            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            buffer = io.BytesIO()
            img.save(buffer, format="PNG", optimize=True)
            self._empty_tile = buffer.getvalue()
        return self._empty_tile
