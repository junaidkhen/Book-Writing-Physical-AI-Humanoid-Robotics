from fastapi import APIRouter
from datetime import datetime
import asyncio
from src.schemas.health_schemas import HealthResponse, HealthStatus
from src.clients.qdrant_client import qdrant_client, check_collection_exists
from src.clients.openai_client import openai_client
from src.config.settings import settings
from src.utils.logging import logger

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_endpoint():
    """
    Check the health of the service and its dependencies.
    """
    # Check Qdrant connectivity
    qdrant_status = "unavailable"
    try:
        # Test connection by getting collection info
        if check_collection_exists(settings.qdrant_collection_name):
            qdrant_status = "available"
        else:
            qdrant_status = "collection missing"
    except Exception as e:
        qdrant_status = f"error: {str(e)}"
        logger.warning(f"Qdrant health check failed: {str(e)}")

    # Check OpenAI connectivity (simple test)
    openai_status = "unavailable"
    try:
        # Make a simple test call to verify API key works
        models = openai_client.models.list()
        openai_status = "available"
    except Exception as e:
        openai_status = f"error: {str(e)}"
        logger.warning(f"OpenAI health check failed: {str(e)}")

    # Determine overall status
    overall_status = HealthStatus.HEALTHY
    if qdrant_status != "available" or openai_status != "available":
        overall_status = HealthStatus.DEGRADED

    # If both are unavailable, mark as unhealthy
    if "error" in qdrant_status and "error" in openai_status:
        overall_status = HealthStatus.UNHEALTHY

    response = HealthResponse(
        status=overall_status,
        qdrant_status=qdrant_status,
        openai_status=openai_status,
        timestamp=datetime.utcnow().isoformat()
    )

    logger.info(f"Health check completed - Status: {overall_status}")
    return response