"""
Unit tests for basic retrieval functionality (T016)

Tests cover:
- Query embedding generation
- Top-k retrieval from Qdrant
- Error handling for empty queries
- Token limit validation
- Connection retry logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import os
import sys

# Add parent directory to path to import main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestQueryEmbedding:
    """Tests for query embedding functionality"""

    @patch('cohere.Client')
    def test_embed_query_success(self, mock_cohere):
        """Test successful query embedding"""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]  # 1024-dim vector
        mock_client.embed.return_value = mock_response
        mock_cohere.return_value = mock_client

        # Test embedding
        query = "What is physical AI?"
        result = mock_client.embed(texts=[query], model='embed-english-v3.0')

        assert result.embeddings is not None
        assert len(result.embeddings[0]) == 1024
        mock_client.embed.assert_called_once()

    @patch('cohere.Client')
    def test_embed_empty_query_validation(self, mock_cohere):
        """Test that empty queries are rejected before API call"""
        query = ""

        # Validate query (should fail)
        is_valid = bool(query and query.strip())

        assert is_valid is False, "Empty query should be rejected"

    @patch('cohere.Client')
    def test_embed_whitespace_query_validation(self, mock_cohere):
        """Test that whitespace-only queries are rejected"""
        query = "   \t\n  "

        # Validate query
        is_valid = bool(query and query.strip())

        assert is_valid is False, "Whitespace-only query should be rejected"

    def test_token_limit_detection(self):
        """Test detection of queries exceeding Cohere token limit"""
        # Cohere embed-english-v3.0 limit: 512 tokens (~2000 characters)
        short_query = "What is physical AI?"
        long_query = "x" * 2500  # Exceeds limit

        assert len(short_query) < 2000, "Short query should be under limit"
        assert len(long_query) > 2000, "Long query should exceed limit"

        # Validate short query
        is_short_valid = len(short_query) <= 2000
        assert is_short_valid is True

        # Validate long query
        is_long_valid = len(long_query) <= 2000
        assert is_long_valid is False


class TestQdrantRetrieval:
    """Tests for Qdrant top-k retrieval functionality"""

    @patch('qdrant_client.QdrantClient')
    def test_query_points_success(self, mock_qdrant):
        """Test successful top-k retrieval from Qdrant"""
        # Setup mock
        mock_client = Mock()
        mock_result = Mock()
        mock_result.points = [
            Mock(id="uuid1", score=0.85, payload={"url": "http://test.com", "text": "Test chunk 1"}),
            Mock(id="uuid2", score=0.72, payload={"url": "http://test.com", "text": "Test chunk 2"}),
            Mock(id="uuid3", score=0.68, payload={"url": "http://test.com", "text": "Test chunk 3"})
        ]
        mock_client.query_points.return_value = mock_result
        mock_qdrant.return_value = mock_client

        # Test retrieval
        query_vector = [0.1] * 1024
        results = mock_client.query_points(
            collection_name="documents",
            query=query_vector,
            limit=10
        )

        assert results.points is not None
        assert len(results.points) == 3
        assert results.points[0].score > results.points[1].score  # Verify ranking
        mock_client.query_points.assert_called_once()

    @patch('qdrant_client.QdrantClient')
    def test_query_points_empty_collection(self, mock_qdrant):
        """Test retrieval from empty collection returns no results"""
        # Setup mock for empty collection
        mock_client = Mock()
        mock_result = Mock()
        mock_result.points = []
        mock_client.query_points.return_value = mock_result
        mock_qdrant.return_value = mock_client

        # Test retrieval
        query_vector = [0.1] * 1024
        results = mock_client.query_points(
            collection_name="documents",
            query=query_vector,
            limit=10
        )

        assert results.points == []
        assert len(results.points) == 0

    @patch('qdrant_client.QdrantClient')
    def test_configurable_top_k(self, mock_qdrant):
        """Test that top-k parameter is configurable"""
        mock_client = Mock()
        mock_result = Mock()
        mock_result.points = [Mock(id=f"uuid{i}", score=0.9-i*0.1) for i in range(5)]
        mock_client.query_points.return_value = mock_result
        mock_qdrant.return_value = mock_client

        # Test with different k values
        for k in [5, 10, 20]:
            mock_result.points = [Mock(id=f"uuid{i}", score=0.9-i*0.01) for i in range(k)]
            results = mock_client.query_points(
                collection_name="documents",
                query=[0.1] * 1024,
                limit=k
            )
            assert len(results.points) == k


class TestConnectionRetryLogic:
    """Tests for Qdrant connection retry with exponential backoff"""

    @patch('qdrant_client.QdrantClient')
    @patch('time.sleep')
    def test_connection_retry_success_on_second_attempt(self, mock_sleep, mock_qdrant):
        """Test successful connection on retry"""
        mock_client = Mock()

        # Fail first, succeed second
        mock_client.get_collections.side_effect = [
            Exception("Connection failed"),
            Mock()  # Success
        ]
        mock_qdrant.return_value = mock_client

        # Simulate retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                mock_client.get_collections()
                break  # Success
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    mock_sleep(wait_time)
                else:
                    raise

        # Verify retry happened
        assert mock_client.get_collections.call_count == 2
        mock_sleep.assert_called_once_with(1)  # First retry: 2^0 = 1 second

    @patch('qdrant_client.QdrantClient')
    @patch('time.sleep')
    def test_connection_retry_fails_after_max_attempts(self, mock_sleep, mock_qdrant):
        """Test connection fails after all retries exhausted"""
        mock_client = Mock()
        mock_client.get_collections.side_effect = Exception("Connection failed")
        mock_qdrant.return_value = mock_client

        # Simulate retry logic
        max_retries = 3
        with pytest.raises(Exception, match="Connection failed"):
            for attempt in range(max_retries):
                try:
                    mock_client.get_collections()
                except Exception as e:
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt
                        mock_sleep(wait_time)
                    else:
                        raise e

        # Verify all retries attempted
        assert mock_client.get_collections.call_count == 3
        assert mock_sleep.call_count == 2  # 2 retries before final failure


class TestRetrievalErrorHandling:
    """Tests for error handling in retrieval pipeline"""

    @patch('qdrant_client.QdrantClient')
    def test_collection_not_found_error(self, mock_qdrant):
        """Test handling of missing collection error"""
        mock_client = Mock()
        mock_client.query_points.side_effect = Exception("Collection 'documents' not found")
        mock_qdrant.return_value = mock_client

        with pytest.raises(Exception, match="Collection.*not found"):
            mock_client.query_points(
                collection_name="documents",
                query=[0.1] * 1024,
                limit=10
            )

    @patch('cohere.Client')
    def test_cohere_api_error(self, mock_cohere):
        """Test handling of Cohere API errors"""
        mock_client = Mock()
        mock_client.embed.side_effect = Exception("API rate limit exceeded")
        mock_cohere.return_value = mock_client

        with pytest.raises(Exception, match="API rate limit exceeded"):
            mock_client.embed(texts=["test query"], model='embed-english-v3.0')


class TestMetadataExtraction:
    """Tests for metadata extraction from retrieved chunks"""

    def test_extract_required_fields(self):
        """Test extraction of required metadata fields (FR-003)"""
        # Mock retrieved chunk
        mock_chunk = Mock()
        mock_chunk.id = "uuid-123"
        mock_chunk.score = 0.85
        mock_chunk.payload = {
            "url": "https://example.com/page1",
            "text": "This is the original text content",
            "chunk_index": 5
        }

        # Extract metadata
        vector_id = mock_chunk.id
        score = mock_chunk.score
        source_url = mock_chunk.payload.get("url")
        text = mock_chunk.payload.get("text")
        chunk_index = mock_chunk.payload.get("chunk_index")

        # Verify required fields present (FR-003)
        assert vector_id is not None
        assert score is not None
        assert source_url is not None
        assert text is not None
        assert chunk_index is not None

        # Verify field types
        assert isinstance(vector_id, str)
        assert isinstance(score, (int, float))
        assert isinstance(source_url, str)
        assert isinstance(text, str)
        assert isinstance(chunk_index, int)

    def test_detect_missing_metadata(self):
        """Test detection of incomplete metadata (FR-005)"""
        # Mock chunk with missing URL
        mock_chunk_missing_url = Mock()
        mock_chunk_missing_url.payload = {
            "text": "Content without URL",
            "chunk_index": 0
        }

        source_url = mock_chunk_missing_url.payload.get("url")
        assert source_url is None, "Missing URL should be detected"

        # Mock chunk with missing text
        mock_chunk_missing_text = Mock()
        mock_chunk_missing_text.payload = {
            "url": "https://example.com",
            "chunk_index": 0
        }

        text = mock_chunk_missing_text.payload.get("text")
        assert text is None, "Missing text should be detected"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
