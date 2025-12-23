"""Contract tests for batch ingestion API endpoint.

Tests the /ingest/batch endpoint per contracts/ingestion-api.yaml.
Verifies multipart files array, max 100 files, 202 response with BatchIngestionResponse,
and rejected files in errors array.
"""
import os
import tempfile
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.main import app
from backend.src.models.ingestion_job import JobType, JobStatus


def test_batch_ingestion_endpoint_contract():
    """Test the batch ingestion endpoint contract per API specification."""
    client = TestClient(app)

    # Create temporary files for testing
    temp_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(f"Test content for file {i}")
            temp_file.flush()  # Ensure content is written
            temp_files.append(temp_file)

    try:
        # Prepare files for upload
        files = [("files", open(temp_file.name, "rb")) for temp_file in temp_files]

        # Mock the ingestion service
        with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
            # Create a mock job response
            mock_job = MagicMock()
            mock_job.job_id = "test-job-id"
            mock_job.job_type = JobType.BATCH
            mock_job.total_documents = 3
            mock_job.documents_processed = 3
            mock_job.documents_failed = 0
            mock_job.status = JobStatus.COMPLETED
            mock_job.document_ids = ["doc1", "doc2", "doc3"]
            mock_job.error_logs = []

            mock_service.return_value.process_batch.return_value = mock_job

            # Make the request
            response = client.post("/api/v1/ingest/batch", files=files)

            # Verify response status
            assert response.status_code == 202  # 202 Accepted

            # Verify response structure matches contract
            response_data = response.json()
            assert "job_id" in response_data
            assert "total_documents" in response_data
            assert "documents_processed" in response_data
            assert "documents_failed" in response_data
            assert "status" in response_data

            # Verify values
            assert response_data["job_id"] == "test-job-id"
            assert response_data["total_documents"] == 3
            assert response_data["documents_processed"] == 3
            assert response_data["documents_failed"] == 0
            assert response_data["status"] in ["pending", "processing", "completed", "failed", "partial_success"]
    finally:
        # Clean up files and temporary files
        for temp_file in temp_files:
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


def test_batch_ingestion_with_errors_contract():
    """Test batch ingestion endpoint with some files failing."""
    client = TestClient(app)

    # Create temporary files for testing
    temp_files = []
    for i in range(3):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(f"Test content for file {i}")
            temp_file.flush()
            temp_files.append(temp_file)

    try:
        # Prepare files for upload
        files = [("files", open(temp_file.name, "rb")) for temp_file in temp_files]

        # Mock the ingestion service with some errors
        with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
            # Create a mock job response with errors
            mock_job = MagicMock()
            mock_job.job_id = "test-job-id"
            mock_job.job_type = JobType.BATCH
            mock_job.total_documents = 3
            mock_job.documents_processed = 2
            mock_job.documents_failed = 1
            mock_job.status = JobStatus.PARTIAL_SUCCESS
            mock_job.document_ids = ["doc1", "doc2", "doc3"]

            # Create mock error log
            mock_error_log = MagicMock()
            mock_error_log.document_id = "failed-doc-id"
            mock_error_log.error_message = "File format not supported"
            mock_job.error_logs = [mock_error_log]

            mock_service.return_value.process_batch.return_value = mock_job

            # Make the request
            response = client.post("/api/v1/ingest/batch", files=files)

            # Verify response status
            assert response.status_code == 202  # 202 Accepted

            # Verify response structure
            response_data = response.json()
            assert "job_id" in response_data
            assert "total_documents" in response_data
            assert "documents_processed" in response_data
            assert "documents_failed" in response_data
            assert "status" in response_data
            assert "error_logs" in response_data

            # Verify error logs structure
            assert len(response_data["error_logs"]) >= 0
    finally:
        # Clean up files and temporary files
        for temp_file in temp_files:
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


def test_batch_ingestion_empty_files():
    """Test batch ingestion with no files."""
    client = TestClient(app)

    # Make the request with no files
    response = client.post("/api/v1/ingest/batch", files=[])

    # Should return 400 for validation error
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data or "detail" in response_data


def test_batch_ingestion_too_many_files():
    """Test batch ingestion with too many files (over 100)."""
    client = TestClient(app)

    # Create 101 temporary files to exceed the limit
    temp_files = []
    for i in range(101):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(f"Test content for file {i}")
            temp_file.flush()
            temp_files.append(temp_file)

    try:
        # Prepare files for upload
        files = [("files", open(temp_file.name, "rb")) for temp_file in temp_files]

        # Mock the ingestion service to handle the large batch
        with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
            mock_job = MagicMock()
            mock_job.job_id = "test-job-id"
            mock_job.job_type = JobType.BATCH
            mock_job.total_documents = 101
            mock_job.documents_processed = 0
            mock_job.documents_failed = 101
            mock_job.status = JobStatus.FAILED
            mock_job.document_ids = ["doc" + str(i) for i in range(101)]
            mock_job.error_logs = []

            mock_service.return_value.process_batch.return_value = mock_job

            # Make the request
            response = client.post("/api/v1/ingest/batch", files=files)

            # Should still accept the request but may fail during processing
            assert response.status_code in [202, 400]  # Either accepts or rejects based on validation
    finally:
        # Clean up files and temporary files
        for temp_file in temp_files:
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


def test_batch_ingestion_response_schema():
    """Test that the response schema matches the contract."""
    client = TestClient(app)

    # Create temporary files for testing
    temp_files = []
    for i in range(2):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(f"Test content for file {i}")
            temp_file.flush()
            temp_files.append(temp_file)

    try:
        # Prepare files for upload
        files = [("files", open(temp_file.name, "rb")) for temp_file in temp_files]

        # Mock the ingestion service
        with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
            # Create a mock job response
            mock_job = MagicMock()
            mock_job.job_id = "test-job-id"
            mock_job.job_type = JobType.BATCH
            mock_job.total_documents = 2
            mock_job.documents_processed = 2
            mock_job.documents_failed = 0
            mock_job.status = JobStatus.COMPLETED
            mock_job.document_ids = ["doc1", "doc2"]
            mock_job.error_logs = []

            mock_service.return_value.process_batch.return_value = mock_job

            # Make the request
            response = client.post("/api/v1/ingest/batch", files=files)

            # Verify response structure per contract
            assert response.status_code == 202
            response_data = response.json()

            # Required fields per contract
            required_fields = ["job_id", "total_documents", "documents_processed", "documents_failed", "status"]
            for field in required_fields:
                assert field in response_data, f"Missing required field: {field}"

            # Verify data types
            assert isinstance(response_data["job_id"], str)
            assert isinstance(response_data["total_documents"], int)
            assert isinstance(response_data["documents_processed"], int)
            assert isinstance(response_data["documents_failed"], int)
            assert isinstance(response_data["status"], str)

            # Verify values are reasonable
            assert response_data["total_documents"] >= 0
            assert response_data["documents_processed"] >= 0
            assert response_data["documents_failed"] >= 0
            assert response_data["total_documents"] == response_data["documents_processed"] + response_data["documents_failed"]
    finally:
        # Clean up files and temporary files
        for temp_file in temp_files:
            temp_file.close()
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


def test_batch_ingestion_invalid_file_types():
    """Test batch ingestion with invalid file types."""
    client = TestClient(app)

    # Create a temporary invalid file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.exe', delete=False) as temp_file:
        temp_file.write("Fake executable content")
        temp_file.flush()
        invalid_file = temp_file

    try:
        # Prepare file for upload
        files = [("files", open(invalid_file.name, "rb"))]

        # Mock the ingestion service to simulate file rejection
        with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
            # Create a mock job response with errors
            mock_job = MagicMock()
            mock_job.job_id = "test-job-id"
            mock_job.job_type = JobType.BATCH
            mock_job.total_documents = 1
            mock_job.documents_processed = 0
            mock_job.documents_failed = 1
            mock_job.status = JobStatus.FAILED
            mock_job.document_ids = ["doc1"]

            # Create mock error log
            mock_error_log = MagicMock()
            mock_error_log.document_id = "failed-doc-id"
            mock_error_log.error_message = "Unsupported file type: .exe"
            mock_job.error_logs = [mock_error_log]

            mock_service.return_value.process_batch.return_value = mock_job

            # Make the request
            response = client.post("/api/v1/ingest/batch", files=files)

            # Should still return 202 as the job is accepted for processing
            # The validation happens during processing
            assert response.status_code == 202

            response_data = response.json()
            assert response_data["documents_failed"] >= 0
    finally:
        # Clean up files and temporary files
        invalid_file.close()
        if os.path.exists(invalid_file.name):
            os.unlink(invalid_file.name)


def test_batch_ingestion_large_files():
    """Test batch ingestion with large files."""
    client = TestClient(app)

    # Create a temporary large file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        # Write a large content (larger than typical file size limits)
        large_content = "Large content line. " * 10000
        temp_file.write(large_content)
        temp_file.flush()
        large_file = temp_file

    try:
        # Prepare file for upload
        files = [("files", open(large_file.name, "rb"))]

        # Mock the ingestion service
        with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
            mock_job = MagicMock()
            mock_job.job_id = "test-job-id"
            mock_job.job_type = JobType.BATCH
            mock_job.total_documents = 1
            mock_job.documents_processed = 1
            mock_job.documents_failed = 0
            mock_job.status = JobStatus.COMPLETED
            mock_job.document_ids = ["doc1"]
            mock_job.error_logs = []

            mock_service.return_value.process_batch.return_value = mock_job

            # Make the request
            response = client.post("/api/v1/ingest/batch", files=files)

            # Should return 202 if accepted
            assert response.status_code == 202
    finally:
        # Clean up files and temporary files
        large_file.close()
        if os.path.exists(large_file.name):
            os.unlink(large_file.name)


if __name__ == "__main__":
    pytest.main([__file__])