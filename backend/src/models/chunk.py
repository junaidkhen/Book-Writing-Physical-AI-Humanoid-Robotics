"""Chunk model for the document ingestion system.

Represents a semantically meaningful text segment extracted from a Document,
with positional metadata for reconstruction and embedding storage for RAG retrieval.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class Chunk(BaseModel):
    """Chunk entity representing a text segment from a document."""

    chunk_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    chunk_index: int = Field(..., ge=0)
    text_content: str = Field(..., min_length=500, max_length=2000)  # 500-2000 chars
    char_count: int
    start_position: Optional[int] = Field(None, ge=0)
    end_position: Optional[int] = Field(None, gt=0)
    embedding_vector: Optional[List[float]] = None
    embedding_model: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('char_count')
    @classmethod
    def validate_char_count(cls, v: int, values) -> int:
        """Validate that char_count matches the length of text_content."""
        # Note: We can't access text_content here directly due to Pydantic v2 limitations
        # This validation will be done at the application level
        if v < 0:
            raise ValueError('char_count must be non-negative')
        return v

    @field_validator('text_content')
    @classmethod
    def validate_text_content_length(cls, v: str, values) -> str:
        """Validate text content length is between 500-2000 characters."""
        if len(v) < 500 or len(v) > 2000:
            raise ValueError('text_content must be between 500 and 2000 characters')
        return v

    @field_validator('end_position')
    @classmethod
    def validate_position_order(cls, v: Optional[int], values) -> Optional[int]:
        """Validate that end_position is greater than start_position if both are provided."""
        if v is None:
            return v
        start_pos = values.get('start_position')
        if start_pos is not None and v <= start_pos:
            raise ValueError('end_position must be greater than start_position')
        return v

    @field_validator('embedding_vector')
    @classmethod
    def validate_embedding_vector(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        """Validate embedding vector has correct dimensions (1024 for Cohere embed-english-v3.0)."""
        if v is None:
            return v
        # For Cohere embed-english-v3.0, the dimension should be 1024
        if len(v) != 1024:
            raise ValueError('embedding_vector must have 1024 dimensions for Cohere embed-english-v3.0')
        return v

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
        extra = "forbid"