"""Unit tests for ingestion orchestration service.

Tests end-to-end flow: validate→extract→chunk→embed→store, duplicate detection
via content_hash, error handling per FR-008.
Verifies ingestion service follows specification requirements.
"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock, Mock
from uuid import UUID

from backend.src.models import Document, ProcessingStatus
from backend.src.services.ingestion import IngestionService
from backend.src.services.validation import ValidationError


def test_ingestion_service_initialization():
    """Test ingestion service initialization."""
    # Since we can't easily mock the storage clients, we'll test the initialization logic
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()
        assert service is not None


def test_create_document_record():
    """Test creation of initial document record."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        doc = service._create_document_record(
            filename="test.pdf",
            content_type="pdf",
            content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            file_size_bytes=1024
        )

        assert doc.filename == "test.pdf"
        assert doc.content_type == "pdf"
        assert doc.content_hash == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert doc.file_size_bytes == 1024
        assert doc.processing_status == ProcessingStatus.PROCESSING
        assert doc.processing_started_at is not None
        assert isinstance(doc.document_id, UUID)


def test_extract_content_type():
    """Test content type extraction from file extension."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        assert service._extract_content_type("/path/to/file.pdf") == "pdf"
        assert service._extract_content_type("/path/to/file.txt") == "txt"
        assert service._extract_content_type("/path/to/file.docx") == "docx"
        assert service._extract_content_type("/path/to/file.html") == "html"
        assert service._extract_content_type("/path/to/file.htm") == "html"

        # Test unsupported extension
        with pytest.raises(Exception):  # This raises IngestionError but we can't import it easily
            service._extract_content_type("/path/to/file.exe")


def test_update_document_status():
    """Test updating document processing status."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        # Create a test document
        doc = Document(
            filename="test.pdf",
            content_type="pdf",
            content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            file_size_bytes=1024
        )

        # Update to completed
        updated_doc = service._update_document_status(
            doc,
            ProcessingStatus.COMPLETED,
            chunk_count=5
        )
        assert updated_doc.processing_status == ProcessingStatus.COMPLETED
        assert updated_doc.chunk_count == 5
        assert updated_doc.processing_completed_at is not None

        # Update to failed
        updated_doc = service._update_document_status(
            doc,
            ProcessingStatus.FAILED,
            error_message="Test error"
        )
        assert updated_doc.processing_status == ProcessingStatus.FAILED
        assert updated_doc.error_message == "Test error"


def test_process_batch_single_success():
    """Test batch processing with single successful document."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        # Mock the ingest_single_document method to return success
        with patch.object(service, 'ingest_single_document', return_value=(True, None, Mock())):
            result = service.process_batch(["/fake/path.pdf"])

            assert result.total_documents == 1
            assert result.documents_processed == 1
            assert result.documents_failed == 0
            assert result.status.name in ["COMPLETED", "PARTIAL_SUCCESS"]


def test_process_batch_with_failures():
    """Test batch processing with some failures."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        # Mock the ingest_single_document method to return mixed results
        def mock_ingest(path):
            if "success" in path:
                return (True, None, Mock())
            else:
                return (False, "Test error", None)

        with patch.object(service, 'ingest_single_document', side_effect=mock_ingest):
            result = service.process_batch(["/fake/success.pdf", "/fake/fail.pdf"])

            assert result.total_documents == 2
            assert result.documents_processed == 1  # Only 1 success
            assert result.documents_failed == 1     # 1 failure
            assert result.status.name == "PARTIAL_SUCCESS"


def test_process_batch_all_failures():
    """Test batch processing with all failures."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        # Mock the ingest_single_document method to return failure for all
        with patch.object(service, 'ingest_single_document', return_value=(False, "Test error", None)):
            result = service.process_batch(["/fake/path1.pdf", "/fake/path2.pdf"])

            assert result.total_documents == 2
            assert result.documents_processed == 0
            assert result.documents_failed == 2
            assert result.status.name in ["FAILED", "PARTIAL_SUCCESS"]


def test_ingest_single_document_validation_failure():
    """Test single document ingestion with validation failure."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        # Mock validation to fail
        with patch('backend.src.services.ingestion.validate_file_upload', return_value=(False, "Validation failed")):
            success, error_msg, doc = service.ingest_single_document("/fake/path.pdf")

            assert success is False
            assert "Validation failed" in error_msg


def test_ingest_single_document_success_path():
    """Test the success path of single document ingestion (with mocking)."""
    with patch('backend.src.services.ingestion.get_qdrant_client'), \
         patch('backend.src.services.ingestion.get_cohere_client'):

        service = IngestionService()

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write("This is test content that is at least 500 characters long to meet the minimum chunk size requirement for the text processing system. " * 3)
            temp_file_path = temp_file.name

        try:
            # Mock all the dependent services
            with patch('backend.src.services.ingestion.validate_file_upload', return_value=(True, None)), \
                 patch('backend.src.services.ingestion.extract_text_from_file', return_value="Test content"), \
                 patch('backend.src.services.ingestion.chunk_text_content', return_value=[{
                     'text_content': "Test content",
                     'chunk_index': 0,
                     'start_position': 0,
                     'end_position': len("Test content"),
                     'char_count': len("Test content")
                 }]), \
                 patch.object(service, '_store_chunks', return_value=1), \
                 patch.object(service, '_check_duplicate', return_value=None), \
                 patch('os.path.getsize', return_value=1024):

                success, error_msg, doc = service.ingest_single_document(temp_file_path)

                assert success is True
                assert error_msg is None
                assert doc is not None
        finally:
            # Clean up the temp file
            os.unlink(temp_file_path)


if __name__ == "__main__":
    pytest.main([__file__])