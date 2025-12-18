from fastapi import APIRouter, Response, HTTPException
from fastapi.responses import JSONResponse

from app.services.tile_renderer import TileRenderer

router = APIRouter()

# Shared tile renderer instance
tile_renderer = TileRenderer()

# Will be set by main.py
current_timestamp = None
data_bounds = {
    "west": -130.0,
    "south": 20.0,
    "east": -60.0,
    "north": 55.0,
}


@router.get("/tiles/{z}/{x}/{y}.png")
async def get_tile(z: int, x: int, y: int) -> Response:
    """
    XYZ tile endpoint for radar data.

    Returns a 256x256 PNG tile with radar reflectivity data.
    Supports zoom levels 0-12 (weather data doesn't need more detail).
    """
    # Validate zoom level
    if z < 0 or z > 14:
        raise HTTPException(status_code=400, detail="Invalid zoom level (0-14)")

    # Validate tile coordinates
    max_tile = 2**z
    if x < 0 or x >= max_tile or y < 0 or y >= max_tile:
        raise HTTPException(status_code=400, detail="Invalid tile coordinates")

    content = tile_renderer.get_tile(z, x, y)

    return Response(
        content=content,
        media_type="image/png",
        headers={
            "Cache-Control": "public, max-age=60",
            "Access-Control-Allow-Origin": "*",
        },
    )


@router.get("/api/metadata")
async def get_metadata() -> JSONResponse:
    """
    Return current data timestamp for cache busting.

    Frontend polls this endpoint to detect new data.
    """
    if current_timestamp is None:
        return JSONResponse(
            {
                "timestamp": None,
                "timestamp_unix": None,
                "status": "no_data",
                "message": "No radar data available yet. Data is being fetched...",
                "bounds": data_bounds,
            }
        )

    return JSONResponse(
        {
            "timestamp": current_timestamp.isoformat(),
            "timestamp_unix": int(current_timestamp.timestamp()),
            "status": "ok",
            "bounds": data_bounds,
        }
    )


@router.get("/api/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse({"status": "healthy"})
