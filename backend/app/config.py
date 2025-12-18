from pathlib import Path
import os

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# NOAA MRMS settings
# Note: URL redirects from /data/2D/ to /2D/
NOAA_BASE_URL = "https://mrms.ncep.noaa.gov/2D/ReflectivityAtLowestAltitude/"
NOAA_LATEST_FILE = "MRMS_ReflectivityAtLowestAltitude.latest.grib2.gz"

# Polling interval in seconds (2 minutes)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 10))

# File paths
LATEST_GEOTIFF = DATA_DIR / "latest_radar.tif"

# Keep last N GRIB2 files for debugging
MAX_GRIB_FILES = 5
