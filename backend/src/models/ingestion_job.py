"""IngestionJob model for the document ingestion system.

Tracks batch ingestion operations processing multiple documents, enabling progress
monitoring, error aggregation, and retry logic.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class JobType(str, Enum):
    """Job type enumeration."""
    SINGLE = "single"
    BATCH = "batch"


class JobStatus(str, Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_SUCCESS = "partial_success"


class ErrorLog(BaseModel):
    """Error log entry for failed documents in an ingestion job."""
    document_id: UUID
    error_message: str


class IngestionJob(BaseModel):
    """IngestionJob entity for tracking batch operations."""

    job_id: UUID = Field(default_factory=uuid4)
    job_type: JobType
    total_documents: int = Field(..., ge=1, le=100)  # Max 100 per FR-010
    documents_processed: int = Field(..., ge=0)
    documents_failed: int = Field(..., ge=0)
    status: JobStatus = JobStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_logs: List[ErrorLog] = Field(default_factory=list)
    document_ids: List[UUID]

    @field_validator('documents_processed', 'documents_failed')
    @classmethod
    def validate_document_counts(cls, v: int) -> int:
        """Validate document counts are non-negative."""
        if v < 0:
            raise ValueError('Document counts must be non-negative')
        return v

    @field_validator('total_documents')
    @classmethod
    def validate_total_documents(cls, v: int) -> int:
        """Validate total documents is within batch limit."""
        if v < 1 or v > 100:  # Per FR-010 batch limit
            raise ValueError('total_documents must be between 1 and 100')
        return v

    @field_validator('document_ids')
    @classmethod
    def validate_document_ids_length(cls, v: List[UUID], values) -> List[UUID]:
        """Validate document IDs list length matches total_documents."""
        total_docs = values.get('total_documents')
        if total_docs is not None and len(v) != total_docs:
            raise ValueError('document_ids length must match total_documents')
        return v

    @field_validator('status')
    @classmethod
    def validate_status_transitions(cls, v: JobStatus, values) -> JobStatus:
        """Validate status based on document counts."""
        documents_processed = values.get('documents_processed', 0)
        documents_failed = values.get('documents_failed', 0)
        total_documents = values.get('total_documents', 0)

        # Validate status based on document counts
        if v == JobStatus.FAILED and documents_processed == 0 and documents_failed == 0:
            raise ValueError('Status cannot be FAILED if no documents failed')

        if v == JobStatus.PARTIAL_SUCCESS and documents_failed == 0:
            raise ValueError('Status cannot be PARTIAL_SUCCESS if no documents failed')

        if v in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.PARTIAL_SUCCESS] and documents_processed + documents_failed != total_documents:
            raise ValueError('documents_processed + documents_failed must equal total_documents when job is completed')

        return v

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
        extra = "forbid"