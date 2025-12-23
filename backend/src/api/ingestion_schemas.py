"""API schemas for the document ingestion system.

Pydantic schemas for request/response validation per contracts/ingestion-api.yaml.
Defines all API data structures for endpoints.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field

from ..models import Document, Chunk, IngestionJob, ProcessingStatus, JobStatus


# Base schemas
class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthStatus(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str]  # Service name to status mapping
    version: str = "0.1.0"


class DependencyStatus(BaseModel):
    """Dependency health status schema."""
    service: str
    status: str
    details: Optional[Dict[str, Any]] = None


# Ingestion-related schemas
class IngestionResponse(BaseModel):
    """Response schema for single document ingestion."""
    document_id: UUID
    filename: str
    content_type: str
    file_size_bytes: int
    content_hash: str
    status: str
    message: str
    processing_started_at: datetime


class BatchIngestionResponse(BaseModel):
    """Response schema for batch document ingestion."""
    job_id: UUID
    total_documents: int
    documents_processed: int
    documents_failed: int
    status: JobStatus
    completed_at: Optional[datetime] = None
    error_logs: List[Dict[str, str]]  # {document_id: error_message}


class JobStatusResponse(BaseModel):
    """Response schema for ingestion job status."""
    job_id: UUID
    status: JobStatus
    total_documents: int
    documents_processed: int
    documents_failed: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_logs: List[Dict[str, str]]


class DocumentResponse(BaseModel):
    """Response schema for document metadata."""
    document_id: UUID
    filename: str
    content_type: str
    content_hash: str
    file_size_bytes: int
    source_url: Optional[str]
    upload_date: datetime
    processing_status: ProcessingStatus
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None
    chunk_count: Optional[int] = None
    error_message: Optional[str] = None
    ingestion_job_id: Optional[UUID] = None

    @classmethod
    def from_document(cls, document: Document) -> 'DocumentResponse':
        """Create DocumentResponse from Document model."""
        return cls(
            document_id=document.document_id,
            filename=document.filename,
            content_type=document.content_type,
            content_hash=document.content_hash,
            file_size_bytes=document.file_size_bytes,
            source_url=document.source_url,
            upload_date=document.upload_date,
            processing_status=document.processing_status,
            processing_started_at=document.processing_started_at,
            processing_completed_at=document.processing_completed_at,
            chunk_count=document.chunk_count,
            error_message=document.error_message,
            ingestion_job_id=document.ingestion_job_id,
        )


class DocumentListResponse(BaseModel):
    """Response schema for list of documents."""
    documents: List[DocumentResponse]
    total: int
    limit: int
    offset: int


class ChunkResponse(BaseModel):
    """Response schema for chunk data."""
    chunk_id: UUID
    document_id: UUID
    chunk_index: int
    text_content: str
    char_count: int
    start_position: Optional[int] = None
    end_position: Optional[int] = None
    embedding_model: Optional[str] = None
    created_at: datetime


class MetricsResponse(BaseModel):
    """Response schema for system metrics."""
    total_documents: int
    total_chunks: int
    avg_processing_time: Optional[float] = None  # seconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IngestionURLRequest(BaseModel):
    """Request schema for URL ingestion."""
    url: str = Field(..., description="URL to ingest content from")


class IngestionURLResponse(BaseModel):
    """Response schema for URL ingestion."""
    document_id: UUID
    url: str
    filename: str
    status: str
    message: str


# Conversion functions
def document_to_response(document: Document) -> DocumentResponse:
    """Convert Document model to DocumentResponse schema."""
    return DocumentResponse.from_document(document)


__all__ = [
    'ErrorResponse',
    'HealthStatus',
    'DependencyStatus',
    'IngestionResponse',
    'BatchIngestionResponse',
    'JobStatusResponse',
    'DocumentResponse',
    'DocumentListResponse',
    'ChunkResponse',
    'MetricsResponse',
    'IngestionURLRequest',
    'IngestionURLResponse',
    'document_to_response',
]