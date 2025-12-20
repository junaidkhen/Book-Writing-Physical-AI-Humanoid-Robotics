"""Unit tests for Document model.

Tests field validation, status transitions, and content_hash uniqueness per data-model.md.
Verifies Document model follows specification requirements.
"""
import pytest
from datetime import datetime
from uuid import UUID

from backend.src.models.document import Document, ProcessingStatus


def test_document_creation_with_required_fields():
    """Test creating a Document with all required fields."""
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        file_size_bytes=1024
    )

    assert document.filename == "test.pdf"
    assert document.content_type == "pdf"
    assert document.content_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert document.file_size_bytes == 1024
    assert document.processing_status == ProcessingStatus.PENDING
    assert isinstance(document.document_id, UUID)
    assert document.upload_date is not None


def test_document_content_hash_validation():
    """Test content hash validation follows SHA-256 format."""
    # Valid SHA-256 hash (64 characters, hex)
    valid_hash = "a" * 64
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash=valid_hash,
        file_size_bytes=1024
    )
    assert document.content_hash == valid_hash

    # Invalid hash (not 64 chars)
    with pytest.raises(ValueError):
        Document(
            filename="test.pdf",
            content_type="pdf",
            content_hash="invalid_hash",
            file_size_bytes=1024
        )


def test_document_content_type_validation():
    """Test content type validation."""
    valid_types = ["pdf", "txt", "docx", "html"]

    for content_type in valid_types:
        document = Document(
            filename="test." + ("txt" if content_type == "txt" else content_type),
            content_type=content_type,
            content_hash="a" * 64,
            file_size_bytes=1024
        )
        assert document.content_type == content_type

    # Invalid content type
    with pytest.raises(ValueError):
        Document(
            filename="test.invalid",
            content_type="invalid",
            content_hash="a" * 64,
            file_size_bytes=1024
        )


def test_document_file_size_validation():
    """Test file size validation."""
    # Valid file size
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash="a" * 64,
        file_size_bytes=1024  # 1KB
    )
    assert document.file_size_bytes == 1024

    # Maximum allowed size (500MB)
    max_size = 524288000  # 500MB in bytes
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash="a" * 64,
        file_size_bytes=max_size
    )
    assert document.file_size_bytes == max_size

    # Invalid file size (too large)
    with pytest.raises(ValueError):
        Document(
            filename="test.pdf",
            content_type="pdf",
            content_hash="a" * 64,
            file_size_bytes=max_size + 1
        )

    # Invalid file size (negative)
    with pytest.raises(ValueError):
        Document(
            filename="test.pdf",
            content_type="pdf",
            content_hash="a" * 64,
            file_size_bytes=-1
        )


def test_document_status_transitions():
    """Test processing status transitions."""
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash="a" * 64,
        file_size_bytes=1024
    )
    assert document.processing_status == ProcessingStatus.PENDING

    # Transition to processing
    document.processing_status = ProcessingStatus.PROCESSING
    assert document.processing_status == ProcessingStatus.PROCESSING

    # Transition to completed
    document.processing_status = ProcessingStatus.COMPLETED
    assert document.processing_status == ProcessingStatus.COMPLETED

    # Transition to failed
    document.processing_status = ProcessingStatus.FAILED
    assert document.processing_status == ProcessingStatus.FAILED


def test_document_optional_fields():
    """Test optional fields can be None."""
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash="a" * 64,
        file_size_bytes=1024,
        source_url=None,
        processing_started_at=None,
        processing_completed_at=None,
        chunk_count=None,
        error_message=None,
        ingestion_job_id=None
    )

    assert document.source_url is None
    assert document.processing_started_at is None
    assert document.processing_completed_at is None
    assert document.chunk_count is None
    assert document.error_message is None
    assert document.ingestion_job_id is None


def test_document_source_url_validation():
    """Test source URL validation."""
    # Valid URL
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash="a" * 64,
        file_size_bytes=1024,
        source_url="https://example.com/document.pdf"
    )
    assert document.source_url == "https://example.com/document.pdf"

    # None is valid
    document = Document(
        filename="test.pdf",
        content_type="pdf",
        content_hash="a" * 64,
        file_size_bytes=1024,
        source_url=None
    )
    assert document.source_url is None

    # Invalid URL (no scheme)
    with pytest.raises(ValueError):
        Document(
            filename="test.pdf",
            content_type="pdf",
            content_hash="a" * 64,
            file_size_bytes=1024,
            source_url="example.com/document.pdf"
        )


if __name__ == "__main__":
    pytest.main([__file__])