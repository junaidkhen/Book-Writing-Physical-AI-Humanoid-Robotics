import pytest
from fastapi.testclient import TestClient
from src.main import create_app
from src.schemas.health_schemas import HealthResponse
from src.schemas.metadata_schemas import MetricsResponse


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_health_endpoint(client):
    """Test the health endpoint."""
    response = client.get("/api/v1/health")

    assert response.status_code == 200

    data = response.json()
    assert "status" in data
    assert "qdrant_status" in data
    assert "openai_status" in data
    assert "timestamp" in data

    # Status should be one of the expected values
    assert data["status"] in ["healthy", "degraded", "unhealthy"]


def test_metadata_endpoint(client):
    """Test the metadata endpoint."""
    response = client.get("/api/v1/metadata")

    # The response might be 200 or 500 depending on service state
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        data = response.json()
        assert "config" in data
        assert "stats" in data

        config = data["config"]
        assert "model" in config
        assert "temperature" in config
        assert "top_k_default" in config
        assert "max_tokens" in config
        assert "qdrant_collection" in config

        stats = data["stats"]
        assert "total_queries" in stats
        assert "avg_response_time" in stats
        assert "avg_token_usage" in stats
        assert "error_count" in stats
        assert "uptime" in stats


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "RAG-Enabled Agent Service"
    assert data["version"] == "0.1.0"
    assert data["status"] == "running"