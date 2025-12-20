from pydantic import BaseModel, Field, validator
from typing import Optional


class QueryRequest(BaseModel):
    """
    Input model for the /ask endpoint
    """
    query: str = Field(..., description="User's natural language question", max_length=1000)
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve (1-20, default 5)")
    temperature: Optional[float] = Field(default=0.1, ge=0.0, le=0.2, description="Temperature for agent response (0.0-0.2, default 0.1)")

    @validator('query')
    def validate_query_length(cls, v):
        if len(v) == 0:
            raise ValueError('Query cannot be empty')
        return v


class RetrievalRequest(BaseModel):
    """
    Input model for the /retrieve endpoint
    """
    query: str = Field(..., description="User's search query", max_length=1000)
    top_k: Optional[int] = Field(default=5, ge=1, le=20, description="Number of chunks to retrieve (1-20, default 5)")

    @validator('query')
    def validate_retrieval_query_length(cls, v):
        if len(v) == 0:
            raise ValueError('Query cannot be empty')
        return v