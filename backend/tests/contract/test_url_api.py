"""Contract tests for URL ingestion API endpoint.

Tests the /ingest/url endpoint per contracts/ingestion-api.yaml.
Verifies JSON request with URL field, 202 response, 400 for invalid/unreachable URLs.
"""
import json
from unittest.mock import patch, MagicMock
import pytest
from fastapi.testclient import TestClient

from backend.src.main import app


def test_url_ingestion_endpoint_contract():
    """Test the URL ingestion endpoint contract per API specification."""
    client = TestClient(app)

    # Test valid URL request
    with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
        # Create a mock response
        mock_doc = MagicMock()
        mock_doc.document_id = "test-doc-id"
        mock_doc.filename = "example.html"
        mock_doc.processing_status = "completed"
        mock_service.return_value.ingest_from_url.return_value = (True, None, mock_doc)

        # Make the request
        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com/document.html"},
            headers={"Content-Type": "application/json"}
        )

        # Verify response status
        assert response.status_code == 202  # 202 Accepted

        # Verify response structure matches contract
        response_data = response.json()
        assert "document_id" in response_data
        assert "url" in response_data
        assert "filename" in response_data
        assert "status" in response_data
        assert "message" in response_data

        # Verify values
        assert response_data["document_id"] == "test-doc-id"
        assert response_data["url"] == "https://example.com/document.html"
        assert response_data["filename"] == "example.html"
        assert response_data["status"] == "success"


def test_url_ingestion_with_invalid_url():
    """Test URL ingestion with invalid URL format."""
    client = TestClient(app)

    # Test with invalid URL format
    response = client.post(
        "/api/v1/ingest/url",
        json={"url": "not-a-valid-url"},
        headers={"Content-Type": "application/json"}
    )

    # Should return 400 for validation error
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data or "detail" in response_data


def test_url_ingestion_with_blocked_private_ip():
    """Test URL ingestion with private IP (SSRF protection)."""
    client = TestClient(app)

    # Test with private IP URL (should be blocked by SSRF protection)
    response = client.post(
        "/api/v1/ingest/url",
        json={"url": "http://192.168.1.1/private-content.html"},
        headers={"Content-Type": "application/json"}
    )

    # Should return 400 for blocked URL
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data or "detail" in response_data


def test_url_ingestion_with_localhost():
    """Test URL ingestion with localhost (SSRF protection)."""
    client = TestClient(app)

    # Test with localhost URL (should be blocked by SSRF protection)
    response = client.post(
        "/api/v1/ingest/url",
        json={"url": "http://localhost:8080/internal-content.html"},
        headers={"Content-Type": "application/json"}
    )

    # Should return 400 for blocked URL
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data or "detail" in response_data


def test_url_ingestion_with_missing_url():
    """Test URL ingestion with missing URL field."""
    client = TestClient(app)

    # Test with missing URL field
    response = client.post(
        "/api/v1/ingest/url",
        json={"other_field": "some-value"},
        headers={"Content-Type": "application/json"}
    )

    # Should return 422 for validation error (missing required field)
    assert response.status_code == 422
    response_data = response.json()
    assert "detail" in response_data


def test_url_ingestion_with_empty_url():
    """Test URL ingestion with empty URL."""
    client = TestClient(app)

    # Test with empty URL
    response = client.post(
        "/api/v1/ingest/url",
        json={"url": ""},
        headers={"Content-Type": "application/json"}
    )

    # Should return 400 for validation error
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data or "detail" in response_data


def test_url_ingestion_with_unreachable_url():
    """Test URL ingestion with unreachable URL (simulated)."""
    client = TestClient(app)

    # Mock the ingestion service to simulate unreachable URL
    with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
        mock_service.return_value.ingest_from_url.return_value = (False, "Failed to fetch URL: Connection refused", None)

        # Make the request
        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://unreachable-example.com/document.html"},
            headers={"Content-Type": "application/json"}
        )

        # Should return 400 for unreachable URL
        assert response.status_code == 400
        response_data = response.json()
        assert "error" in response_data or "detail" in response_data


def test_url_ingestion_response_schema():
    """Test that the response schema matches the contract."""
    client = TestClient(app)

    # Mock successful ingestion
    with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
        mock_doc = MagicMock()
        mock_doc.document_id = "valid-test-id"
        mock_doc.filename = "test-file.html"
        mock_doc.processing_status = "completed"
        mock_service.return_value.ingest_from_url.return_value = (True, None, mock_doc)

        # Make the request
        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com/test.html"},
            headers={"Content-Type": "application/json"}
        )

        # Verify response structure per contract
        assert response.status_code == 202
        response_data = response.json()

        # Required fields per contract
        required_fields = ["document_id", "url", "filename", "status", "message"]
        for field in required_fields:
            assert field in response_data, f"Missing required field: {field}"

        # Verify data types
        assert isinstance(response_data["document_id"], str)
        assert isinstance(response_data["url"], str)
        assert isinstance(response_data["filename"], str)
        assert isinstance(response_data["status"], str)
        assert isinstance(response_data["message"], str)

        # Verify values are reasonable
        assert response_data["document_id"] == "valid-test-id"
        assert response_data["url"] == "https://example.com/test.html"
        assert response_data["filename"] == "test-file.html"
        assert response_data["status"] == "success"


def test_url_ingestion_http_vs_https():
    """Test URL ingestion with both HTTP and HTTPS schemes."""
    client = TestClient(app)

    # Test with HTTP URL
    with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
        mock_doc = MagicMock()
        mock_doc.document_id = "http-test-id"
        mock_doc.filename = "http-file.html"
        mock_doc.processing_status = "completed"
        mock_service.return_value.ingest_from_url.return_value = (True, None, mock_doc)

        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "http://example.com/document.html"},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 202
        response_data = response.json()
        assert response_data["url"] == "http://example.com/document.html"

    # Test with HTTPS URL
    with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
        mock_doc = MagicMock()
        mock_doc.document_id = "https-test-id"
        mock_doc.filename = "https-file.html"
        mock_doc.processing_status = "completed"
        mock_service.return_value.ingest_from_url.return_value = (True, None, mock_doc)

        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://secure-example.com/document.html"},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 202
        response_data = response.json()
        assert response_data["url"] == "https://secure-example.com/document.html"


def test_url_ingestion_with_special_characters():
    """Test URL ingestion with URLs containing special characters."""
    client = TestClient(app)

    # Test with URL containing query parameters and special characters
    with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
        mock_doc = MagicMock()
        mock_doc.document_id = "special-test-id"
        mock_doc.filename = "special-file.html"
        mock_doc.processing_status = "completed"
        mock_service.return_value.ingest_from_url.return_value = (True, None, mock_doc)

        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com/path?param=value&other=123#section"},
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 202
        response_data = response.json()
        assert response_data["url"] == "https://example.com/path?param=value&other=123#section"


def test_url_ingestion_with_invalid_scheme():
    """Test URL ingestion with invalid scheme (should be blocked)."""
    client = TestClient(app)

    # Test with FTP URL (should be blocked)
    response = client.post(
        "/api/v1/ingest/url",
        json={"url": "ftp://example.com/file.txt"},
        headers={"Content-Type": "application/json"}
    )

    # Should return 400 for invalid scheme
    assert response.status_code == 400
    response_data = response.json()
    assert "error" in response_data or "detail" in response_data


def test_url_ingestion_without_content_type_header():
    """Test URL ingestion without Content-Type header."""
    client = TestClient(app)

    # Make request without explicit Content-Type (FastAPI should handle this)
    with patch('backend.src.services.ingestion.get_ingestion_service') as mock_service:
        mock_doc = MagicMock()
        mock_doc.document_id = "content-type-test-id"
        mock_doc.filename = "ct-file.html"
        mock_doc.processing_status = "completed"
        mock_service.return_value.ingest_from_url.return_value = (True, None, mock_doc)

        response = client.post(
            "/api/v1/ingest/url",
            json={"url": "https://example.com/document.html"}
            # No Content-Type header specified
        )

        # Should still work (FastAPI infers Content-Type for JSON)
        assert response.status_code == 202
        response_data = response.json()
        assert response_data["document_id"] == "content-type-test-id"


if __name__ == "__main__":
    pytest.main([__file__])