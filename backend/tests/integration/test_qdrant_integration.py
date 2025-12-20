"""Integration tests for Qdrant storage service

Tests per T012 requirements:
- Mock Qdrant responses
- Test connection
- Collection creation
- Batch upsert
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

from backend.src.services.storage import QdrantStorage, CohereEmbeddings


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing"""
    with patch('backend.src.services.storage.QdrantClient') as mock_client:
        yield mock_client


@pytest.fixture
def qdrant_storage(mock_qdrant_client):
    """Create QdrantStorage instance with mocked client"""
    return QdrantStorage(url="http://localhost:6333")


class TestQdrantConnection:
    """Test Qdrant client initialization and connection"""

    def test_client_initialization(self, qdrant_storage, mock_qdrant_client):
        """Test that Qdrant client initializes correctly"""
        assert qdrant_storage.collection_name == "documents"
        assert qdrant_storage.client is not None
        mock_qdrant_client.assert_called_once()

    def test_client_with_api_key(self, mock_qdrant_client):
        """Test client initialization with API key"""
        storage = QdrantStorage(
            url="http://localhost:6333",
            api_key="test-api-key"
        )

        mock_qdrant_client.assert_called_with(
            url="http://localhost:6333",
            api_key="test-api-key",
            timeout=30
        )

    def test_custom_collection_name(self, mock_qdrant_client):
        """Test custom collection name"""
        storage = QdrantStorage(
            url="http://localhost:6333",
            collection_name="custom_collection"
        )

        assert storage.collection_name == "custom_collection"


class TestCollectionManagement:
    """Test collection creation and management"""

    def test_create_collection_new(self, qdrant_storage):
        """Test creating a new collection"""
        # Mock get_collections to return empty list
        mock_collections = Mock()
        mock_collections.collections = []
        qdrant_storage.client.get_collections = Mock(return_value=mock_collections)

        qdrant_storage.create_collection(vector_size=1024)

        # Verify create_collection was called
        qdrant_storage.client.create_collection.assert_called_once()
        call_kwargs = qdrant_storage.client.create_collection.call_args[1]
        assert call_kwargs['collection_name'] == "documents"

    def test_create_collection_already_exists(self, qdrant_storage):
        """Test that existing collection is not recreated"""
        # Mock collection already exists
        mock_collection = Mock()
        mock_collection.name = "documents"
        mock_collections = Mock()
        mock_collections.collections = [mock_collection]
        qdrant_storage.client.get_collections = Mock(return_value=mock_collections)

        qdrant_storage.create_collection()

        # Should not call create_collection if already exists
        qdrant_storage.client.create_collection.assert_not_called()

    def test_create_collection_custom_vector_size(self, qdrant_storage):
        """Test collection creation with custom vector size"""
        mock_collections = Mock()
        mock_collections.collections = []
        qdrant_storage.client.get_collections = Mock(return_value=mock_collections)

        qdrant_storage.create_collection(vector_size=512)

        qdrant_storage.client.create_collection.assert_called_once()


class TestBatchUpsert:
    """Test batch upsert operations"""

    def test_upsert_empty_chunks(self, qdrant_storage):
        """Test upsert with empty list returns 0"""
        result = qdrant_storage.upsert_chunks([])
        assert result == 0

    def test_upsert_single_chunk(self, qdrant_storage):
        """Test upserting single chunk"""
        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "document_id": str(uuid.uuid4()),
            "chunk_index": 0,
            "text_content": "Test content",
            "char_count": 12,
            "embedding_vector": [0.1] * 1024,
            "embedding_model": "embed-english-v3.0",
            "document_metadata": {
                "filename": "test.pdf",
                "content_type": "pdf"
            }
        }

        result = qdrant_storage.upsert_chunks([chunk])

        assert result == 1
        qdrant_storage.client.upsert.assert_called_once()

    def test_upsert_batch_chunks(self, qdrant_storage):
        """Test upserting multiple chunks in batches"""
        chunks = []
        for i in range(150):  # More than default batch size (100)
            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "document_id": str(uuid.uuid4()),
                "chunk_index": i,
                "text_content": f"Content {i}",
                "char_count": len(f"Content {i}"),
                "embedding_vector": [0.1] * 1024,
                "embedding_model": "embed-english-v3.0",
                "document_metadata": {}
            })

        result = qdrant_storage.upsert_chunks(chunks, batch_size=100)

        assert result == 150
        # Should be called twice (100 + 50)
        assert qdrant_storage.client.upsert.call_count == 2

    def test_upsert_chunk_payload_structure(self, qdrant_storage):
        """Test that upserted chunk has correct payload structure"""
        chunk_id = str(uuid.uuid4())
        document_id = str(uuid.uuid4())

        chunk = {
            "chunk_id": chunk_id,
            "document_id": document_id,
            "chunk_index": 0,
            "text_content": "Test content",
            "char_count": 12,
            "start_position": 0,
            "end_position": 12,
            "embedding_vector": [0.1] * 1024,
            "embedding_model": "embed-english-v3.0",
            "created_at": "2025-12-17T10:00:00Z",
            "document_metadata": {
                "filename": "test.pdf",
                "content_type": "pdf",
                "content_hash": "abc123"
            }
        }

        qdrant_storage.upsert_chunks([chunk])

        # Verify payload structure in upsert call
        call_args = qdrant_storage.client.upsert.call_args
        points = call_args[1]['points']

        assert len(points) == 1
        point = points[0]
        assert point.id == chunk_id
        assert point.vector == chunk["embedding_vector"]
        assert point.payload["document_id"] == document_id
        assert point.payload["text_content"] == "Test content"
        assert point.payload["document_metadata"]["filename"] == "test.pdf"


class TestChunkRetrieval:
    """Test chunk retrieval operations"""

    def test_get_chunk_by_id_found(self, qdrant_storage):
        """Test retrieving existing chunk"""
        chunk_id = str(uuid.uuid4())
        mock_point = Mock()
        mock_point.id = chunk_id
        mock_point.vector = [0.1] * 1024
        mock_point.payload = {
            "document_id": str(uuid.uuid4()),
            "text_content": "Test content",
            "chunk_index": 0
        }

        qdrant_storage.client.retrieve = Mock(return_value=[mock_point])

        result = qdrant_storage.get_chunk_by_id(chunk_id)

        assert result is not None
        assert result["chunk_id"] == chunk_id
        assert result["text_content"] == "Test content"

    def test_get_chunk_by_id_not_found(self, qdrant_storage):
        """Test retrieving non-existent chunk"""
        qdrant_storage.client.retrieve = Mock(return_value=[])

        result = qdrant_storage.get_chunk_by_id("non-existent-id")

        assert result is None

    def test_search_similar_chunks(self, qdrant_storage):
        """Test vector similarity search"""
        query_vector = [0.5] * 1024

        mock_result = Mock()
        mock_result.id = str(uuid.uuid4())
        mock_result.score = 0.95
        mock_result.payload = {
            "text_content": "Similar content",
            "document_metadata": {"filename": "test.pdf"}
        }

        qdrant_storage.client.search = Mock(return_value=[mock_result])

        results = qdrant_storage.search_similar_chunks(
            query_vector,
            limit=5,
            score_threshold=0.7
        )

        assert len(results) == 1
        assert results[0]["score"] == 0.95
        assert results[0]["text_content"] == "Similar content"

    def test_delete_document_chunks(self, qdrant_storage):
        """Test deleting all chunks for a document"""
        document_id = str(uuid.uuid4())

        result = qdrant_storage.delete_document_chunks(document_id)

        qdrant_storage.client.delete.assert_called_once()
        assert result == 1  # Qdrant doesn't return count


class TestErrorHandling:
    """Test error handling in Qdrant operations"""

    def test_create_collection_error(self, qdrant_storage):
        """Test error handling during collection creation"""
        qdrant_storage.client.get_collections = Mock(
            side_effect=Exception("Connection failed")
        )

        with pytest.raises(Exception, match="Connection failed"):
            qdrant_storage.create_collection()

    def test_upsert_error(self, qdrant_storage):
        """Test error handling during upsert"""
        chunk = {
            "chunk_id": str(uuid.uuid4()),
            "document_id": str(uuid.uuid4()),
            "chunk_index": 0,
            "text_content": "Test",
            "char_count": 4,
            "embedding_vector": [0.1] * 1024,
        }

        qdrant_storage.client.upsert = Mock(
            side_effect=Exception("Upsert failed")
        )

        with pytest.raises(Exception, match="Upsert failed"):
            qdrant_storage.upsert_chunks([chunk])

    def test_search_error(self, qdrant_storage):
        """Test error handling during search"""
        qdrant_storage.client.search = Mock(
            side_effect=Exception("Search failed")
        )

        with pytest.raises(Exception, match="Search failed"):
            qdrant_storage.search_similar_chunks([0.1] * 1024)
