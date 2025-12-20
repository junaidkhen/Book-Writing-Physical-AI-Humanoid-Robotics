import pytest
from unittest.mock import AsyncMock, patch
from src.services.retrieval_service import retrieve_chunks, validate_retrieval_parameters
from src.schemas.response_schemas import RetrievedChunk, ChunkMetadata


@pytest.mark.asyncio
async def test_retrieve_chunks_success():
    """Test successful chunk retrieval."""
    with patch('src.services.retrieval_service.qdrant_client') as mock_client:
        # Mock the query_points response
        mock_result = AsyncMock()
        mock_result.points = [
            type('obj', (object,), {
                'id': 'chunk1',
                'payload': {
                    'content': 'Test content 1',
                    'chapter': 'Chapter 1',
                    'section': 'Section 1.1',
                    'source_document': 'doc1'
                },
                'score': 0.9
            })(),
            type('obj', (object,), {
                'id': 'chunk2',
                'payload': {
                    'content': 'Test content 2',
                    'chapter': 'Chapter 2',
                    'section': 'Section 2.1',
                    'source_document': 'doc2'
                },
                'score': 0.8
            })()
        ]
        mock_client.query_points.return_value = mock_result

        chunks, retrieval_time = await retrieve_chunks("test query", top_k=2)

        assert len(chunks) == 2
        assert chunks[0].chunk_id == 'chunk1'
        assert chunks[0].content == 'Test content 1'
        assert chunks[0].score == 0.9
        assert chunks[1].chunk_id == 'chunk2'


def test_validate_retrieval_parameters_valid():
    """Test validation with valid parameters."""
    # Should not raise an exception
    validate_retrieval_parameters("valid query", 5)


def test_validate_retrieval_parameters_invalid_query():
    """Test validation with empty query."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        validate_retrieval_parameters("", 5)

    with pytest.raises(ValueError, match="Query cannot be empty"):
        validate_retrieval_parameters("   ", 5)


def test_validate_retrieval_parameters_invalid_top_k():
    """Test validation with invalid top_k."""
    with pytest.raises(ValueError, match="top_k must be between 1 and 20"):
        validate_retrieval_parameters("valid query", 0)

    with pytest.raises(ValueError, match="top_k must be between 1 and 20"):
        validate_retrieval_parameters("valid query", 25)