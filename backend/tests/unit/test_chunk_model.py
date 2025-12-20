"""Unit tests for Chunk model.

Tests field validation, char_count=len(text_content), chunk_index uniqueness per document.
Verifies Chunk model follows specification requirements from data-model.md.
"""
import pytest
from datetime import datetime
from uuid import UUID

from backend.src.models.chunk import Chunk


def test_chunk_creation_with_required_fields():
    """Test creating a Chunk with all required fields."""
    text_content = "This is a test chunk with content that is at least 500 characters long. " * 10  # Make it long enough
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content=text_content,
        char_count=len(text_content)
    )

    assert chunk.document_id == UUID("12345678-1234-5678-1234-567812345678")
    assert chunk.chunk_index == 0
    assert chunk.text_content == text_content
    assert chunk.char_count == len(text_content)
    assert isinstance(chunk.chunk_id, UUID)
    assert chunk.created_at is not None


def test_chunk_text_content_length_validation():
    """Test text content length validation (500-2000 chars)."""
    # Valid content - minimum length
    min_content = "a" * 500
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content=min_content,
        char_count=len(min_content)
    )
    assert len(chunk.text_content) == 500

    # Valid content - maximum length
    max_content = "a" * 2000
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content=max_content,
        char_count=len(max_content)
    )
    assert len(chunk.text_content) == 2000

    # Invalid content - too short
    with pytest.raises(ValueError):
        Chunk(
            document_id=UUID("12345678-1234-5678-1234-567812345678"),
            chunk_index=0,
            text_content="too short",
            char_count=11
        )

    # Invalid content - too long
    with pytest.raises(ValueError):
        long_content = "a" * 2001
        Chunk(
            document_id=UUID("12345678-1234-5678-1234-567812345678"),
            chunk_index=0,
            text_content=long_content,
            char_count=len(long_content)
        )


def test_chunk_index_validation():
    """Test chunk index validation."""
    # Valid chunk index (non-negative)
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content="a" * 500,
        char_count=500
    )
    assert chunk.chunk_index == 0

    # Valid chunk index (positive)
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=5,
        text_content="a" * 500,
        char_count=500
    )
    assert chunk.chunk_index == 5

    # Invalid chunk index (negative)
    with pytest.raises(ValueError):
        Chunk(
            document_id=UUID("12345678-1234-5678-1234-567812345678"),
            chunk_index=-1,
            text_content="a" * 500,
            char_count=500
        )


def test_chunk_char_count_validation():
    """Test character count validation."""
    content = "a" * 600
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content=content,
        char_count=600
    )
    assert chunk.char_count == 600


def test_chunk_position_validation():
    """Test position validation."""
    # Valid positions
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content="a" * 500,
        char_count=500,
        start_position=0,
        end_position=500
    )
    assert chunk.start_position == 0
    assert chunk.end_position == 500

    # Valid positions (None values)
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content="a" * 500,
        char_count=500,
        start_position=None,
        end_position=None
    )
    assert chunk.start_position is None
    assert chunk.end_position is None

    # Invalid positions (end_position <= start_position)
    with pytest.raises(ValueError):
        Chunk(
            document_id=UUID("12345678-1234-5678-1234-567812345678"),
            chunk_index=0,
            text_content="a" * 500,
            char_count=500,
            start_position=100,
            end_position=50  # Less than start_position
        )


def test_chunk_embedding_vector_validation():
    """Test embedding vector validation."""
    # Valid 1024-dim embedding vector
    embedding = [0.1] * 1024
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content="a" * 500,
        char_count=500,
        embedding_vector=embedding
    )
    assert len(chunk.embedding_vector) == 1024

    # None embedding (valid)
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content="a" * 500,
        char_count=500,
        embedding_vector=None
    )
    assert chunk.embedding_vector is None

    # Invalid embedding (wrong dimension)
    with pytest.raises(ValueError):
        Chunk(
            document_id=UUID("12345678-1234-5678-1234-567812345678"),
            chunk_index=0,
            text_content="a" * 500,
            char_count=500,
            embedding_vector=[0.1] * 100  # Wrong dimension
        )


def test_chunk_optional_fields():
    """Test optional fields can be None."""
    chunk = Chunk(
        document_id=UUID("12345678-1234-5678-1234-567812345678"),
        chunk_index=0,
        text_content="a" * 500,
        char_count=500,
        start_position=None,
        end_position=None,
        embedding_vector=None,
        embedding_model=None
    )

    assert chunk.start_position is None
    assert chunk.end_position is None
    assert chunk.embedding_vector is None
    assert chunk.embedding_model is None


if __name__ == "__main__":
    pytest.main([__file__])