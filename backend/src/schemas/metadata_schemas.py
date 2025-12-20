from pydantic import BaseModel, Field
from typing import Optional
from .response_schemas import TokenUsage


class ServiceConfig(BaseModel):
    """
    Current service configuration
    """
    model: str = Field(..., description="OpenAI model being used")
    temperature: float = Field(..., description="Current temperature setting", ge=0.0, le=0.2)
    top_k_default: int = Field(..., description="Default top-k value", ge=1, le=20)
    max_tokens: int = Field(..., description="Maximum token limit", ge=0)
    qdrant_collection: str = Field(..., description="Qdrant collection name")


class PerformanceStats(BaseModel):
    """
    Performance and usage statistics
    """
    total_queries: int = Field(..., description="Total number of queries processed", ge=0)
    avg_response_time: float = Field(..., description="Average response time in ms", ge=0)
    avg_token_usage: TokenUsage = Field(..., description="Average token usage")
    error_count: int = Field(..., description="Total number of errors", ge=0)
    uptime: str = Field(..., description="Service uptime string")


class MetricsResponse(BaseModel):
    """
    Output model for the /metadata endpoint
    """
    config: ServiceConfig = Field(..., description="Current service configuration")
    stats: PerformanceStats = Field(..., description="Performance and usage statistics")