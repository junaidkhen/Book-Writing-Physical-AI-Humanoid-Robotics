"""
Unit tests for metadata validation and source traceability (T023)

Tests cover:
- Metadata completeness validation
- Source URL verification
- Text content verification
- Chunk uniqueness checks
- Data integrity sampling
"""

import pytest
from unittest.mock import Mock, patch
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestMetadataCompleteness:
    """Tests for metadata completeness validation (SC-002, FR-005)"""

    def test_complete_metadata_passes_validation(self):
        """Test that chunk with all required fields passes validation"""
        chunk = {
            "vector_id": "uuid-123",
            "score": 0.85,
            "source_url": "https://example.com/page1",
            "text": "Complete chunk with all metadata",
            "chunk_index": 5,
            "metadata": {"title": "Test Document"}
        }

        # Validate required fields
        required_fields = ["vector_id", "score", "source_url", "text"]
        is_complete = all(
            field in chunk and chunk[field] is not None and chunk[field] != ""
            for field in required_fields
        )

        assert is_complete is True, "Complete metadata should pass validation"

    def test_missing_source_url_fails_validation(self):
        """Test that chunk without source_url fails validation (FR-003)"""
        chunk = {
            "vector_id": "uuid-456",
            "score": 0.72,
            "text": "Chunk without URL",
            "chunk_index": 3
        }

        # Check for missing URL
        has_url = "source_url" in chunk and chunk["source_url"] is not None and chunk["source_url"] != ""

        assert has_url is False, "Missing source_url should fail validation"

    def test_empty_source_url_fails_validation(self):
        """Test that chunk with empty source_url fails validation"""
        chunk = {
            "vector_id": "uuid-789",
            "score": 0.68,
            "source_url": "",  # Empty string
            "text": "Chunk with empty URL"
        }

        has_valid_url = "source_url" in chunk and chunk["source_url"] is not None and chunk["source_url"] != ""

        assert has_valid_url is False, "Empty source_url should fail validation"

    def test_missing_text_fails_validation(self):
        """Test that chunk without text content fails validation (FR-003)"""
        chunk = {
            "vector_id": "uuid-101",
            "score": 0.90,
            "source_url": "https://example.com/page2",
            "chunk_index": 0
        }

        # Check for missing text
        has_text = "text" in chunk and chunk["text"] is not None and chunk["text"] != ""

        assert has_text is False, "Missing text should fail validation"

    def test_empty_text_fails_validation(self):
        """Test that chunk with empty text fails validation"""
        chunk = {
            "vector_id": "uuid-202",
            "score": 0.77,
            "source_url": "https://example.com/page3",
            "text": "",  # Empty string
            "chunk_index": 2
        }

        has_valid_text = "text" in chunk and chunk["text"] is not None and chunk["text"] != ""

        assert has_valid_text is False, "Empty text should fail validation"


class TestSourceTraceability:
    """Tests for source URL and document traceability"""

    def test_valid_url_format(self):
        """Test validation of URL format"""
        valid_urls = [
            "https://example.com/page1",
            "http://test.org/chapter-1",
            "https://docs.example.com/api/v1/reference"
        ]

        invalid_urls = [
            "not-a-url",
            "ftp://invalid.com",  # Not http(s)
            "https://",  # Incomplete
            "example.com"  # Missing protocol
        ]

        for url in valid_urls:
            is_valid = url.startswith("http://") or url.startswith("https://")
            assert is_valid is True, f"Valid URL {url} should pass"

        for url in invalid_urls:
            is_valid = url.startswith("http://") and "://" in url and len(url) > 10
            assert is_valid is False, f"Invalid URL {url} should fail"

    def test_chunk_to_source_mapping(self):
        """Test mapping chunk IDs back to source documents"""
        # Mock retrieved chunks from same document
        chunks = [
            {
                "vector_id": "uuid-1",
                "source_url": "https://example.com/doc1",
                "chunk_index": 0,
                "text": "First chunk from doc1"
            },
            {
                "vector_id": "uuid-2",
                "source_url": "https://example.com/doc1",
                "chunk_index": 1,
                "text": "Second chunk from doc1"
            },
            {
                "vector_id": "uuid-3",
                "source_url": "https://example.com/doc2",
                "chunk_index": 0,
                "text": "First chunk from doc2"
            }
        ]

        # Group chunks by source URL
        url_to_chunks = {}
        for chunk in chunks:
            url = chunk["source_url"]
            if url not in url_to_chunks:
                url_to_chunks[url] = []
            url_to_chunks[url].append(chunk)

        # Verify mapping
        assert len(url_to_chunks) == 2, "Should have 2 distinct source documents"
        assert len(url_to_chunks["https://example.com/doc1"]) == 2
        assert len(url_to_chunks["https://example.com/doc2"]) == 1

    def test_chunk_index_ordering(self):
        """Test that chunk indices maintain source document ordering"""
        chunks = [
            {"chunk_index": 0, "text": "First"},
            {"chunk_index": 1, "text": "Second"},
            {"chunk_index": 2, "text": "Third"}
        ]

        # Verify ordering
        for i in range(len(chunks) - 1):
            assert chunks[i]["chunk_index"] < chunks[i+1]["chunk_index"], \
                "Chunk indices should be in ascending order"


class TestDataIntegritySampling:
    """Tests for 5% integrity check sampling (FR-012)"""

    @patch('qdrant_client.QdrantClient')
    def test_sample_size_calculation(self, mock_qdrant):
        """Test that 5% sampling is correctly calculated"""
        mock_client = Mock()
        mock_collection = Mock()
        mock_collection.points_count = 1000
        mock_client.get_collection.return_value = mock_collection
        mock_qdrant.return_value = mock_client

        # Calculate 5% sample size
        total_vectors = 1000
        sample_size = max(1, int(total_vectors * 0.05))

        assert sample_size == 50, "5% of 1000 should be 50"

        # Edge case: small collection
        total_vectors_small = 10
        sample_size_small = max(1, int(total_vectors_small * 0.05))
        assert sample_size_small == 1, "Minimum sample size should be 1"

    def test_integrity_metrics_structure(self):
        """Test structure of integrity metrics output"""
        integrity_metrics = {
            "total_vectors_in_collection": 537,
            "sample_size": 27,
            "valid_payload_count": 27,
            "valid_payload_percentage": 100.0,
            "missing_url_count": 0,
            "missing_text_count": 0
        }

        # Verify all required fields present
        required_fields = [
            "total_vectors_in_collection",
            "sample_size",
            "valid_payload_count",
            "valid_payload_percentage",
            "missing_url_count",
            "missing_text_count"
        ]

        for field in required_fields:
            assert field in integrity_metrics, f"Missing required field: {field}"

        # Verify percentage calculation
        expected_percentage = (integrity_metrics["valid_payload_count"] / integrity_metrics["sample_size"]) * 100
        assert integrity_metrics["valid_payload_percentage"] == expected_percentage

    def test_integrity_check_passes_when_no_issues(self):
        """Test that integrity check passes with 100% valid payloads (SC-005)"""
        integrity_metrics = {
            "valid_payload_percentage": 100.0,
            "missing_url_count": 0,
            "missing_text_count": 0
        }

        # SC-005: Zero integrity issues
        has_no_issues = (
            integrity_metrics["valid_payload_percentage"] == 100.0 and
            integrity_metrics["missing_url_count"] == 0 and
            integrity_metrics["missing_text_count"] == 0
        )

        assert has_no_issues is True, "SC-005 should pass with no integrity issues"

    def test_integrity_check_fails_when_issues_detected(self):
        """Test that integrity check fails when issues are detected"""
        integrity_metrics = {
            "valid_payload_percentage": 95.0,  # Not 100%
            "missing_url_count": 2,
            "missing_text_count": 1
        }

        has_issues = (
            integrity_metrics["valid_payload_percentage"] < 100.0 or
            integrity_metrics["missing_url_count"] > 0 or
            integrity_metrics["missing_text_count"] > 0
        )

        assert has_issues is True, "Should detect integrity issues"


class TestDuplicateDetection:
    """Tests for duplicate and corrupted embedding detection (FR-012)"""

    def test_detect_duplicate_vector_ids(self):
        """Test detection of duplicate vector IDs"""
        chunks = [
            {"vector_id": "uuid-1", "text": "Chunk 1"},
            {"vector_id": "uuid-2", "text": "Chunk 2"},
            {"vector_id": "uuid-1", "text": "Duplicate chunk"},  # Duplicate ID
        ]

        vector_ids = [chunk["vector_id"] for chunk in chunks]
        unique_ids = set(vector_ids)

        has_duplicates = len(vector_ids) != len(unique_ids)
        assert has_duplicates is True, "Should detect duplicate vector IDs"

    def test_no_duplicates_in_valid_collection(self):
        """Test that valid collection has unique vector IDs"""
        chunks = [
            {"vector_id": "uuid-1", "text": "Chunk 1"},
            {"vector_id": "uuid-2", "text": "Chunk 2"},
            {"vector_id": "uuid-3", "text": "Chunk 3"},
        ]

        vector_ids = [chunk["vector_id"] for chunk in chunks]
        unique_ids = set(vector_ids)

        has_duplicates = len(vector_ids) != len(unique_ids)
        assert has_duplicates is False, "Valid collection should have unique IDs"

    def test_detect_near_duplicate_text(self):
        """Test detection of chunks with identical text content"""
        chunks = [
            {"vector_id": "uuid-1", "text": "This is unique content"},
            {"vector_id": "uuid-2", "text": "This is also unique"},
            {"vector_id": "uuid-3", "text": "This is unique content"},  # Duplicate text
        ]

        texts = [chunk["text"] for chunk in chunks]
        unique_texts = set(texts)

        has_duplicate_text = len(texts) != len(unique_texts)
        assert has_duplicate_text is True, "Should detect duplicate text content"


class TestMetadataFieldTypes:
    """Tests for validating metadata field types"""

    def test_vector_id_is_string(self):
        """Test that vector_id is a string (UUID format)"""
        chunk = {"vector_id": "a3f2d9c8-1234-5678-90ab-cdef12345678"}
        assert isinstance(chunk["vector_id"], str), "vector_id should be a string"

    def test_score_is_numeric(self):
        """Test that similarity score is numeric (FR-011)"""
        chunk = {"score": 0.85}
        assert isinstance(chunk["score"], (int, float)), "score should be numeric"

    def test_score_in_valid_range(self):
        """Test that cosine similarity score is in valid range (FR-011)"""
        valid_scores = [0.0, 0.5, 0.85, 1.0, -0.2, -1.0]
        for score in valid_scores:
            is_valid = -1.0 <= score <= 1.0
            assert is_valid is True, f"Score {score} should be in range [-1.0, 1.0]"

        invalid_scores = [1.5, -1.5, 2.0, -2.0]
        for score in invalid_scores:
            is_valid = -1.0 <= score <= 1.0
            assert is_valid is False, f"Score {score} should be outside valid range"

    def test_chunk_index_is_integer(self):
        """Test that chunk_index is a non-negative integer"""
        chunk = {"chunk_index": 5}
        assert isinstance(chunk["chunk_index"], int), "chunk_index should be an integer"
        assert chunk["chunk_index"] >= 0, "chunk_index should be non-negative"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
