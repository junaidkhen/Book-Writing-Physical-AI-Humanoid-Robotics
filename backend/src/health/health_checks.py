from typing import Dict, Any, Optional
from ..clients.qdrant_client import qdrant_client, check_collection_exists
from ..clients.openai_client import openai_client
from ..config.settings import settings
from ..utils.logging import logger


async def check_qdrant_health() -> Dict[str, Any]:
    """
    Check the health of the Qdrant connection.
    """
    try:
        # Test connection by getting collection info
        if check_collection_exists(settings.qdrant_collection_name):
            collection_info = qdrant_client.get_collection(settings.qdrant_collection_name)
            return {
                "status": "available",
                "collection_name": settings.qdrant_collection_name,
                "vectors_count": collection_info.points_count,
                "indexed_vectors_count": getattr(collection_info, 'indexed_vectors_count', 0),
                "time": "ok"
            }
        else:
            return {
                "status": "collection_missing",
                "collection_name": settings.qdrant_collection_name,
                "error": f"Collection '{settings.qdrant_collection_name}' does not exist"
            }
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


async def check_openai_health() -> Dict[str, Any]:
    """
    Check the health of the OpenAI connection.
    """
    try:
        # Make a simple test call to verify API key works
        models = openai_client.models.list()
        return {
            "status": "available",
            "models_count": len(models.data),
            "time": "ok"
        }
    except Exception as e:
        logger.error(f"OpenAI health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


async def check_all_services_health() -> Dict[str, Any]:
    """
    Check the health of all services and dependencies.
    """
    qdrant_result = await check_qdrant_health()
    openai_result = await check_openai_health()

    # Determine overall health status
    if qdrant_result["status"] == "error" and openai_result["status"] == "error":
        overall_status = "unhealthy"
    elif qdrant_result["status"] == "error" or openai_result["status"] == "error":
        overall_status = "degraded"
    elif qdrant_result["status"] == "collection_missing":
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return {
        "overall_status": overall_status,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
        "services": {
            "qdrant": qdrant_result,
            "openai": openai_result
        }
    }