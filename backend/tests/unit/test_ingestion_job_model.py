"""Unit tests for IngestionJob model.

Tests field validation, status transitions, and document count constraints per data-model.md.
Verifies documents_processed + documents_failed ≤ total_documents constraint.
"""
import pytest
from datetime import datetime
from uuid import UUID, uuid4

from backend.src.models.ingestion_job import IngestionJob, JobType, JobStatus, ErrorLog


def test_ingestion_job_creation():
    """Test basic IngestionJob creation with valid data."""
    job = IngestionJob(
        job_type=JobType.BATCH,
        total_documents=5,
        documents_processed=0,
        documents_failed=0,
        document_ids=[uuid4() for _ in range(5)]
    )

    assert job.job_type == JobType.BATCH
    assert job.total_documents == 5
    assert job.documents_processed == 0
    assert job.documents_failed == 0
    assert job.status == JobStatus.PENDING
    assert job.started_at is not None
    assert job.completed_at is None
    assert len(job.document_ids) == 5
    assert len(job.error_logs) == 0
    assert isinstance(job.job_id, UUID)


def test_ingestion_job_field_validation():
    """Test field validation constraints."""
    # Test total_documents range (1-100)
    with pytest.raises(ValueError, match="total_documents must be between 1 and 100"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=0,
            documents_processed=0,
            documents_failed=0,
            document_ids=[]
        )

    with pytest.raises(ValueError, match="total_documents must be between 1 and 100"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=101,
            documents_processed=0,
            documents_failed=0,
            document_ids=[uuid4() for _ in range(101)]
        )

    # Test document counts non-negative
    with pytest.raises(ValueError, match="Document counts must be non-negative"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=5,
            documents_processed=-1,
            documents_failed=0,
            document_ids=[uuid4() for _ in range(5)]
        )

    with pytest.raises(ValueError, match="Document counts must be non-negative"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=5,
            documents_processed=0,
            documents_failed=-1,
            document_ids=[uuid4() for _ in range(5)]
        )


def test_document_ids_length_validation():
    """Test that document_ids length matches total_documents."""
    with pytest.raises(ValueError, match="document_ids length must match total_documents"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=5,
            documents_processed=0,
            documents_failed=0,
            document_ids=[uuid4() for _ in range(3)]  # Only 3 IDs for 5 total
        )


def test_status_transitions_validation():
    """Test status validation based on document counts."""
    # Test FAILED status with no failed documents
    with pytest.raises(ValueError, match="Status cannot be FAILED if no documents failed"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=5,
            documents_processed=0,
            documents_failed=0,
            status=JobStatus.FAILED,
            document_ids=[uuid4() for _ in range(5)]
        )

    # Test PARTIAL_SUCCESS status with no failed documents
    with pytest.raises(ValueError, match="Status cannot be PARTIAL_SUCCESS if no documents failed"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=5,
            documents_processed=5,
            documents_failed=0,
            status=JobStatus.PARTIAL_SUCCESS,
            document_ids=[uuid4() for _ in range(5)]
        )

    # Test completed statuses with mismatched document counts
    with pytest.raises(ValueError, match="documents_processed \\+ documents_failed must equal total_documents"):
        IngestionJob(
            job_type=JobType.BATCH,
            total_documents=5,
            documents_processed=3,
            documents_failed=1,
            status=JobStatus.COMPLETED,  # Completed requires all documents processed
            document_ids=[uuid4() for _ in range(5)]
        )


def test_status_transitions_valid():
    """Test valid status transitions."""
    # Test COMPLETED status (all documents processed)
    job = IngestionJob(
        job_type=JobType.BATCH,
        total_documents=5,
        documents_processed=5,
        documents_failed=0,
        status=JobStatus.COMPLETED,
        document_ids=[uuid4() for _ in range(5)]
    )
    assert job.status == JobStatus.COMPLETED

    # Test FAILED status (all documents failed)
    job = IngestionJob(
        job_type=JobType.BATCH,
        total_documents=5,
        documents_processed=0,
        documents_failed=5,
        status=JobStatus.FAILED,
        document_ids=[uuid4() for _ in range(5)]
    )
    assert job.status == JobStatus.FAILED

    # Test PARTIAL_SUCCESS status (some processed, some failed)
    job = IngestionJob(
        job_type=JobType.BATCH,
        total_documents=5,
        documents_processed=3,
        documents_failed=2,
        status=JobStatus.PARTIAL_SUCCESS,
        document_ids=[uuid4() for _ in range(5)]
    )
    assert job.status == JobStatus.PARTIAL_SUCCESS


def test_error_logs_functionality():
    """Test error logs functionality."""
    doc_id = uuid4()
    error_log = ErrorLog(
        document_id=doc_id,
        error_message="Test error message"
    )

    job = IngestionJob(
        job_type=JobType.BATCH,
        total_documents=2,
        documents_processed=1,
        documents_failed=1,
        error_logs=[error_log],
        document_ids=[uuid4(), uuid4()]
    )

    assert len(job.error_logs) == 1
    assert job.error_logs[0].document_id == doc_id
    assert job.error_logs[0].error_message == "Test error message"


def test_job_type_enum():
    """Test JobType enum values."""
    assert JobType.SINGLE.value == "single"
    assert JobType.BATCH.value == "batch"

    # Test that both values are available
    assert JobType("single") == JobType.SINGLE
    assert JobType("batch") == JobType.BATCH


def test_job_status_enum():
    """Test JobStatus enum values."""
    assert JobStatus.PENDING.value == "pending"
    assert JobStatus.PROCESSING.value == "processing"
    assert JobStatus.COMPLETED.value == "completed"
    assert JobStatus.FAILED.value == "failed"
    assert JobStatus.PARTIAL_SUCCESS.value == "partial_success"

    # Test all values are available
    assert JobStatus("pending") == JobStatus.PENDING
    assert JobStatus("processing") == JobStatus.PROCESSING
    assert JobStatus("completed") == JobStatus.COMPLETED
    assert JobStatus("failed") == JobStatus.FAILED
    assert JobStatus("partial_success") == JobStatus.PARTIAL_SUCCESS


def test_datetime_fields():
    """Test datetime field functionality."""
    now = datetime.utcnow()
    job = IngestionJob(
        job_type=JobType.BATCH,
        total_documents=2,
        documents_processed=1,
        documents_failed=1,
        started_at=now,
        completed_at=now,
        document_ids=[uuid4(), uuid4()]
    )

    assert job.started_at == now
    assert job.completed_at == now


def test_json_serialization():
    """Test JSON serialization of IngestionJob."""
    job = IngestionJob(
        job_type=JobType.BATCH,
        total_documents=2,
        documents_processed=1,
        documents_failed=1,
        document_ids=[uuid4(), uuid4()]
    )

    # Test that it can be serialized to dict
    job_dict = job.model_dump()
    assert 'job_id' in job_dict
    assert 'job_type' in job_dict
    assert 'total_documents' in job_dict
    assert job_dict['total_documents'] == 2
    assert job_dict['documents_processed'] == 1
    assert job_dict['documents_failed'] == 1
    assert job_dict['status'] == 'pending'

    # Test that UUIDs are properly serialized to strings
    assert isinstance(job_dict['job_id'], str)
    assert len(job_dict['document_ids']) == 2
    assert all(isinstance(doc_id, str) for doc_id in job_dict['document_ids'])


if __name__ == "__main__":
    pytest.main([__file__])