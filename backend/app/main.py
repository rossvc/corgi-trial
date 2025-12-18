import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes
from app.services.fetcher import MRMSFetcher
from app.services.grib_processor import GRIBProcessor
from app.config import POLL_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global service instances
fetcher: MRMSFetcher = None
processor: GRIBProcessor = None


async def process_new_data():
    """Background task that watches for new GRIB2 files and processes them."""
    global fetcher, processor

    last_processed = None

    while True:
        try:
            # Check if there's a new file to process
            if fetcher.current_file and fetcher.current_file != last_processed:
                result = processor.process_grib(fetcher.current_file)

                if result:
                    # Update the timestamp in routes module
                    routes.current_timestamp = fetcher.current_timestamp
                    last_processed = fetcher.current_file
                    logger.info(
                        f"Data updated: {fetcher.current_timestamp.isoformat()}"
                    )

        except Exception as e:
            logger.error(f"Processing error: {e}")

        await asyncio.sleep(5)  # Check every 5 seconds


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    global fetcher, processor

    logger.info("Starting Weather Radar Tile Server...")

    # Initialize services
    fetcher = MRMSFetcher()
    processor = GRIBProcessor()

    # Start background tasks
    polling_task = asyncio.create_task(fetcher.start_polling())
    processing_task = asyncio.create_task(process_new_data())

    logger.info(f"Background tasks started (polling every {POLL_INTERVAL}s)")

    yield

    # Shutdown
    logger.info("Shutting down...")
    fetcher.stop()
    polling_task.cancel()
    processing_task.cancel()

    try:
        await polling_task
    except asyncio.CancelledError:
        pass

    try:
        await processing_task
    except asyncio.CancelledError:
        pass


# Create FastAPI app
app = FastAPI(
    title="Weather Radar Tile Server",
    description="Serves MRMS radar data as XYZ map tiles",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router)


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Weather Radar Tile Server",
        "version": "1.0.0",
        "endpoints": {
            "tiles": "/tiles/{z}/{x}/{y}.png",
            "metadata": "/api/metadata",
            "health": "/api/health",
        },
    }
