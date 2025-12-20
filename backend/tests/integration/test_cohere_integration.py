"""Integration tests for Cohere embeddings service

Tests per T014 requirements:
- Mock Cohere API
- Test embedding dimension=1024
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from backend.src.services.storage import CohereEmbeddings


@pytest.fixture
def mock_cohere_client():
    """Mock Cohere client for testing"""
    with patch('backend.src.services.storage.cohere.Client') as mock_client:
        yield mock_client


@pytest.fixture
def cohere_embeddings(mock_cohere_client):
    """Create CohereEmbeddings instance with mocked client"""
    return CohereEmbeddings(api_key="test-api-key")


class TestCohereInitialization:
    """Test Cohere client initialization"""

    def test_client_initialization_default_model(self, cohere_embeddings, mock_cohere_client):
        """Test initialization with default model"""
        assert cohere_embeddings.model == "embed-english-v3.0"
        mock_cohere_client.assert_called_once_with("test-api-key")

    def test_client_initialization_custom_model(self, mock_cohere_client):
        """Test initialization with custom model"""
        embeddings = CohereEmbeddings(
            api_key="test-api-key",
            model="embed-multilingual-v3.0"
        )

        assert embeddings.model == "embed-multilingual-v3.0"


class TestEmbeddingGeneration:
    """Test embedding generation"""

    def test_embed_single_text(self, cohere_embeddings):
        """Test embedding a single text"""
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts(["Test text"])

        assert len(result) == 1
        assert len(result[0]) == 1024
        cohere_embeddings.client.embed.assert_called_once_with(
            texts=["Test text"],
            model="embed-english-v3.0",
            input_type="search_document"
        )

    def test_embed_multiple_texts(self, cohere_embeddings):
        """Test embedding multiple texts in batch"""
        texts = [
            "First chunk of text",
            "Second chunk of text",
            "Third chunk of text"
        ]

        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024, [0.2] * 1024, [0.3] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts(texts)

        assert len(result) == 3
        assert all(len(emb) == 1024 for emb in result)

    def test_embed_empty_list(self, cohere_embeddings):
        """Test embedding empty list returns empty list"""
        result = cohere_embeddings.embed_texts([])

        assert result == []
        cohere_embeddings.client.embed.assert_not_called()

    def test_embed_query_single(self, cohere_embeddings):
        """Test embedding a single query"""
        mock_response = Mock()
        mock_response.embeddings = [[0.5] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_query("What is physical AI?")

        assert len(result) == 1024
        cohere_embeddings.client.embed.assert_called_once_with(
            texts=["What is physical AI?"],
            model="embed-english-v3.0",
            input_type="search_query"
        )

    def test_embed_with_search_document_input_type(self, cohere_embeddings):
        """Test embedding with search_document input type"""
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        cohere_embeddings.embed_texts(
            ["Document text"],
            input_type="search_document"
        )

        call_kwargs = cohere_embeddings.client.embed.call_args[1]
        assert call_kwargs['input_type'] == "search_document"

    def test_embed_with_classification_input_type(self, cohere_embeddings):
        """Test embedding with classification input type"""
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        cohere_embeddings.embed_texts(
            ["Text to classify"],
            input_type="classification"
        )

        call_kwargs = cohere_embeddings.client.embed.call_args[1]
        assert call_kwargs['input_type'] == "classification"


class TestEmbeddingDimensions:
    """Test embedding dimension validation"""

    def test_embedding_dimension_1024(self, cohere_embeddings):
        """Test that embeddings have 1024 dimensions per data-model.md"""
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts(["Test"])

        assert len(result[0]) == 1024

    def test_embedding_dimension_mismatch_warning(self, cohere_embeddings, caplog):
        """Test warning when embedding dimension is not 1024"""
        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 512]  # Wrong dimension
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts(["Test"])

        # Should still return the embeddings
        assert len(result[0]) == 512

        # But should log a warning
        assert "Expected 1024 dimensions, got 512" in caplog.text

    def test_batch_embeddings_consistent_dimensions(self, cohere_embeddings):
        """Test that all embeddings in batch have same dimensions"""
        mock_response = Mock()
        mock_response.embeddings = [
            [0.1] * 1024,
            [0.2] * 1024,
            [0.3] * 1024
        ]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts(["Text 1", "Text 2", "Text 3"])

        assert all(len(emb) == 1024 for emb in result)


class TestErrorHandling:
    """Test error handling in Cohere operations"""

    def test_embed_api_error(self, cohere_embeddings):
        """Test error handling when Cohere API fails"""
        cohere_embeddings.client.embed = Mock(
            side_effect=Exception("API rate limit exceeded")
        )

        with pytest.raises(Exception, match="API rate limit exceeded"):
            cohere_embeddings.embed_texts(["Test"])

    def test_embed_authentication_error(self, cohere_embeddings):
        """Test error handling for authentication failures"""
        cohere_embeddings.client.embed = Mock(
            side_effect=Exception("Invalid API key")
        )

        with pytest.raises(Exception, match="Invalid API key"):
            cohere_embeddings.embed_texts(["Test"])

    def test_embed_network_error(self, cohere_embeddings):
        """Test error handling for network failures"""
        cohere_embeddings.client.embed = Mock(
            side_effect=Exception("Connection timeout")
        )

        with pytest.raises(Exception, match="Connection timeout"):
            cohere_embeddings.embed_texts(["Test"])

    def test_embed_query_error(self, cohere_embeddings):
        """Test error handling in embed_query"""
        cohere_embeddings.client.embed = Mock(
            side_effect=Exception("API error")
        )

        with pytest.raises(Exception, match="API error"):
            cohere_embeddings.embed_query("Test query")


class TestLargeInputs:
    """Test handling of large text inputs"""

    def test_embed_very_long_text(self, cohere_embeddings):
        """Test embedding very long text (simulated)"""
        long_text = "This is a test. " * 1000  # ~16,000 chars

        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts([long_text])

        assert len(result) == 1
        assert len(result[0]) == 1024

    def test_embed_many_texts(self, cohere_embeddings):
        """Test embedding large batch of texts"""
        texts = [f"Text {i}" for i in range(100)]

        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024] * 100
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts(texts)

        assert len(result) == 100

    def test_embed_unicode_text(self, cohere_embeddings):
        """Test embedding text with Unicode characters"""
        unicode_text = "Physical AI: 物理AI and Robotics 🤖"

        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]
        cohere_embeddings.client.embed = Mock(return_value=mock_response)

        result = cohere_embeddings.embed_texts([unicode_text])

        assert len(result) == 1
        assert len(result[0]) == 1024


class TestModelConfiguration:
    """Test different model configurations"""

    def test_default_model_embed_english_v3(self, mock_cohere_client):
        """Test default model is embed-english-v3.0"""
        embeddings = CohereEmbeddings(api_key="test-key")
        assert embeddings.model == "embed-english-v3.0"

    def test_custom_model_multilingual(self, mock_cohere_client):
        """Test using multilingual model"""
        embeddings = CohereEmbeddings(
            api_key="test-key",
            model="embed-multilingual-v3.0"
        )

        mock_response = Mock()
        mock_response.embeddings = [[0.1] * 1024]
        embeddings.client.embed = Mock(return_value=mock_response)

        embeddings.embed_texts(["Test"])

        call_kwargs = embeddings.client.embed.call_args[1]
        assert call_kwargs['model'] == "embed-multilingual-v3.0"
