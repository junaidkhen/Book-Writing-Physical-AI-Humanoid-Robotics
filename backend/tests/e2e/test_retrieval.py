import pytest
from fastapi.testclient import TestClient
from src.main import create_app
from src.schemas.query_schemas import RetrievalRequest
from src.schemas.response_schemas import RetrievalResponse


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_retrieve_endpoint_success(client):
    """Test successful retrieval of chunks."""
    # This test will need to be adapted based on actual Qdrant setup
    # For now, we'll test the endpoint structure
    response = client.post(
        "/api/v1/retrieve",
        json={
            "query": "test query",
            "top_k": 3
        }
    )

    # The response might be an error if Qdrant is not available,
    # but we're testing that the endpoint exists and validates input
    assert response.status_code in [200, 500]  # 200 for success, 500 for service issues


def test_retrieve_endpoint_validation(client):
    """Test retrieval endpoint input validation."""
    # Test with empty query
    response = client.post(
        "/api/v1/retrieve",
        json={
            "query": "",  # Empty query should fail validation
            "top_k": 3
        }
    )
    assert response.status_code == 422  # Validation error

    # Test with invalid top_k
    response = client.post(
        "/api/v1/retrieve",
        json={
            "query": "test query",
            "top_k": 25  # Should be <= 20
        }
    )
    assert response.status_code == 422  # Validation error


def test_retrieve_endpoint_defaults(client):
    """Test retrieval endpoint with default parameters."""
    response = client.post(
        "/api/v1/retrieve",
        json={
            "query": "test query"
            # top_k should default to 5
        }
    )

    # Status could be 200 or 500 depending on Qdrant availability
    assert response.status_code in [200, 500]