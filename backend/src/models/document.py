"""Document model for the document ingestion system.

Represents a single ingested file (PDF, TXT, DOCX, HTML, or URL content) with metadata
for tracking, deduplication, and retrieval filtering.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ProcessingStatus(str, Enum):
    """Processing status enumeration for documents."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(BaseModel):
    """Document entity representing an ingested file with metadata."""

    document_id: UUID = Field(default_factory=uuid4)
    filename: str = Field(..., max_length=255)
    content_type: str = Field(..., pattern=r"^(pdf|txt|docx|html)$")
    content_hash: str = Field(..., min_length=64, max_length=64)  # SHA-256 hash
    file_size_bytes: int = Field(..., gt=0, le=524288000)  # Max 500MB
    source_url: Optional[str] = None
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    chunk_count: Optional[int] = Field(None, ge=0)
    error_message: Optional[str] = Field(None, max_length=1000)
    ingestion_job_id: Optional[UUID] = None
    # Optional metadata fields per US4 requirements
    title: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = Field(None, max_length=255)
    creation_date: Optional[datetime] = None

    @field_validator('content_hash')
    @classmethod
    def validate_content_hash(cls, v: str) -> str:
        """Validate that content hash is a valid SHA-256 hex string."""
        if not v:
            return v
        # Check if it's a valid hex string of 64 characters (SHA-256)
        if len(v) != 64 or not all(c in '0123456789abcdef' for c in v.lower()):
            raise ValueError('content_hash must be a valid SHA-256 hex string')
        return v

    @field_validator('source_url')
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate URL format if provided."""
        if v is None:
            return v
        # Basic URL validation - check for http/https scheme
        if not v.startswith(('http://', 'https://')):
            raise ValueError('source_url must be a valid http or https URL')
        return v

    @field_validator('file_size_bytes')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """Validate file size is within limits."""
        if v <= 0 or v > 524288000:  # 500MB in bytes
            raise ValueError('file_size_bytes must be > 0 and <= 500MB')
        return v

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
        # Allow extra fields during development, but restrict in production
        extra = "forbid"