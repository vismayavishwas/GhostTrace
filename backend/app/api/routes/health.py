from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint confirming FastAPI backend operational status."""
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
