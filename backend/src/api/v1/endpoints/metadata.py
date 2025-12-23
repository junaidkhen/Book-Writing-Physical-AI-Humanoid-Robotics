from fastapi import APIRouter
from src.schemas.metadata_schemas import MetricsResponse, ServiceConfig, PerformanceStats
from src.utils.metrics import metrics_tracker
from src.config.settings import settings
from src.utils.logging import logger

router = APIRouter()


@router.get("/metadata", response_model=MetricsResponse)
async def metadata_endpoint():
    """
    Get service configuration and performance metrics.
    """
    # Get current metrics
    current_metrics = metrics_tracker.get_metrics()

    # Create service configuration
    service_config = ServiceConfig(
        model=settings.openai_model,
        temperature=settings.temperature,
        top_k_default=settings.top_k,
        max_tokens=settings.max_tokens,
        qdrant_collection=settings.qdrant_collection_name
    )

    # Create performance statistics
    performance_stats = PerformanceStats(
        total_queries=current_metrics.total_queries,
        avg_response_time=current_metrics.avg_response_time(),
        avg_token_usage=current_metrics.avg_token_usage(),
        error_count=current_metrics.total_errors,
        uptime=current_metrics.uptime()
    )

    response = MetricsResponse(
        config=service_config,
        stats=performance_stats
    )

    logger.info(f"Metadata requested - Total queries: {current_metrics.total_queries}")
    return response