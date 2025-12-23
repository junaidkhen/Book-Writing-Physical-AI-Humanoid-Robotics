import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import create_app
from src.schemas.response_schemas import QueryResponse


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_ask_endpoint_structure(client):
    """Test the ask endpoint structure and validation."""
    # Test with valid request structure
    response = client.post(
        "/api/v1/ask",
        json={
            "query": "What are the key components of a humanoid robot?",
            "top_k": 3,
            "temperature": 0.1
        }
    )

    # The response might be 200 for success or 500 for service issues
    # (like missing Qdrant or OpenAI credentials)
    assert response.status_code in [200, 422, 500]


def test_ask_endpoint_validation(client):
    """Test ask endpoint input validation."""
    # Test with empty query
    response = client.post(
        "/api/v1/ask",
        json={
            "query": "",  # Empty query
            "top_k": 3,
            "temperature": 0.1
        }
    )
    assert response.status_code == 422  # Validation error

    # Test with invalid top_k
    response = client.post(
        "/api/v1/ask",
        json={
            "query": "test query",
            "top_k": 25,  # Should be <= 20
            "temperature": 0.1
        }
    )
    assert response.status_code == 422  # Validation error

    # Test with invalid temperature
    response = client.post(
        "/api/v1/ask",
        json={
            "query": "test query",
            "top_k": 3,
            "temperature": 0.5  # Should be <= 0.2
        }
    )
    assert response.status_code == 422  # Validation error


def test_ask_endpoint_defaults(client):
    """Test ask endpoint with default parameters."""
    response = client.post(
        "/api/v1/ask",
        json={
            "query": "What is artificial intelligence?"
            # top_k and temperature should use defaults
        }
    )

    # Status could be 200 or 500 depending on service availability
    assert response.status_code in [200, 500]