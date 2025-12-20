from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthResponse(BaseModel):
    """
    Output model for the /health endpoint
    """
    status: HealthStatus = Field(..., description="Overall service status")
    qdrant_status: str = Field(..., description="Qdrant connectivity status")
    openai_status: str = Field(..., description="OpenAI API connectivity status")
    timestamp: str = Field(..., description="ISO 8601 timestamp")