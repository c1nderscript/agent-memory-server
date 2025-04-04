import time

from fastapi import APIRouter

from redis_memory_server.models import HealthCheckResponse


router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def get_health():
    """
    Health check endpoint

    Returns:
        HealthCheckResponse with current timestamp
    """
    # Return current time in milliseconds
    return HealthCheckResponse(now=int(time.time() * 1000))
