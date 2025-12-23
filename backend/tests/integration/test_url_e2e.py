"""End-to-end integration test for URL-based ingestion.

Test HTML page ingestion, PDF file download, redirect handling, SSRF protection blocks private IPs.
"""
import tempfile
from unittest.mock import patch, MagicMock
import pytest

from backend.src.models import ProcessingStatus
from backend.src.services.ingestion import IngestionService
from backend.src.services.extraction import TextExtractor, URLContentExtractor


def test_html_page_ingestion():
    """Test HTML page ingestion functionality."""
    ingestion_service = IngestionService()

    # Mock the URL content fetching and text extraction
    with patch.object(URLContentExtractor, 'save_url_content_to_temp_file') as mock_save:
        with patch.object(TextExtractor, 'extract_from_html') as mock_extract:
            # Create a temporary file to simulate downloaded content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write("""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Test HTML Page</title>
                </head>
                <body>
                    <h1>Test Content</h1>
                    <p>This is test content for HTML page ingestion.</p>
                </body>
                </html>
                """)
                temp_file_path = temp_file.name

            mock_save.return_value = temp_file_path
            mock_extract.return_value = "Test Content This is test content for HTML page ingestion."

            # Test the URL ingestion
            success, error_msg, document = ingestion_service.ingest_from_url("https://example.com/test.html")

            # Verify the ingestion was successful
            assert success is True
            assert error_msg is None
            assert document is not None
            assert document.processing_status == ProcessingStatus.COMPLETED
            assert document.filename.endswith('.html')
            assert document.content_type == 'html'

    # Clean up temporary file
    import os
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_pdf_file_download_ingestion():
    """Test PDF file download and ingestion functionality."""
    ingestion_service = IngestionService()

    # Mock the URL content fetching and text extraction
    with patch.object(URLContentExtractor, 'save_url_content_to_temp_file') as mock_save:
        with patch.object(TextExtractor, 'extract_from_pdf') as mock_extract:
            # Create a temporary file to simulate downloaded PDF content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as temp_file:
                temp_file.write("%PDF-1.4 fake PDF content")
                temp_file_path = temp_file.name

            mock_save.return_value = temp_file_path
            mock_extract.return_value = "Fake PDF content for testing."

            # Test the URL ingestion
            success, error_msg, document = ingestion_service.ingest_from_url("https://example.com/test.pdf")

            # Verify the ingestion was successful
            assert success is True
            assert error_msg is None
            assert document is not None
            assert document.processing_status == ProcessingStatus.COMPLETED
            assert document.filename.endswith('.pdf')
            assert document.content_type == 'pdf'

    # Clean up temporary file
    import os
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_redirect_handling():
    """Test redirect handling during URL ingestion."""
    ingestion_service = IngestionService()

    # Mock the URL content fetching with redirect handling
    with patch.object(URLContentExtractor, 'save_url_content_to_temp_file') as mock_save:
        with patch.object(TextExtractor, 'extract_from_html') as mock_extract:
            # Create a temporary file to simulate downloaded content after redirect
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write("""
                <!DOCTYPE html>
                <html>
                <body>
                    <p>Content from redirected URL</p>
                </body>
                </html>
                """)
                temp_file_path = temp_file.name

            mock_save.return_value = temp_file_path
            mock_extract.return_value = "Content from redirected URL"

            # Test the URL ingestion with redirect
            success, error_msg, document = ingestion_service.ingest_from_url("https://example.com/redirect")

            # Verify the ingestion was successful
            assert success is True
            assert error_msg is None
            assert document is not None
            assert document.processing_status == ProcessingStatus.COMPLETED
            assert document.filename.endswith('.html')
            assert document.source_url == "https://example.com/redirect"

    # Clean up temporary file
    import os
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_ssrf_protection_blocks_private_ips():
    """Test that SSRF protection blocks private IP addresses."""
    ingestion_service = IngestionService()

    # Test with private IP URL (should be blocked)
    success, error_msg, document = ingestion_service.ingest_from_url("http://192.168.1.1/private-content.html")

    # Verify the ingestion was blocked
    assert success is False
    assert error_msg is not None
    assert "SSRF" in error_msg or "private" in error_msg or "blocked" in error_msg
    assert document is None


def test_ssrf_protection_blocks_localhost():
    """Test that SSRF protection blocks localhost."""
    ingestion_service = IngestionService()

    # Test with localhost URL (should be blocked)
    success, error_msg, document = ingestion_service.ingest_from_url("http://localhost:8080/internal.html")

    # Verify the ingestion was blocked
    assert success is False
    assert error_msg is not None
    assert "localhost" in error_msg or "SSRF" in error_msg or "blocked" in error_msg
    assert document is None


def test_ssrf_protection_blocks_127_0_0_1():
    """Test that SSRF protection blocks 127.0.0.1."""
    ingestion_service = IngestionService()

    # Test with 127.0.0.1 URL (should be blocked)
    success, error_msg, document = ingestion_service.ingest_from_url("http://127.0.0.1:8080/internal.html")

    # Verify the ingestion was blocked
    assert success is False
    assert error_msg is not None
    assert "127.0.0.1" in error_msg or "SSRF" in error_msg or "blocked" in error_msg
    assert document is None


def test_ssrf_protection_blocks_10_network():
    """Test that SSRF protection blocks 10.x.x.x network."""
    ingestion_service = IngestionService()

    # Test with 10.x.x.x URL (should be blocked)
    success, error_msg, document = ingestion_service.ingest_from_url("http://10.0.0.1:8080/internal.html")

    # Verify the ingestion was blocked
    assert success is False
    assert error_msg is not None
    assert "10." in error_msg or "SSRF" in error_msg or "blocked" in error_msg
    assert document is None


def test_ssrf_protection_blocks_172_network():
    """Test that SSRF protection blocks 172.16-31.x.x network."""
    ingestion_service = IngestionService()

    # Test with 172.16.x.x URL (should be blocked)
    success, error_msg, document = ingestion_service.ingest_from_url("http://172.16.0.1:8080/internal.html")

    # Verify the ingestion was blocked
    assert success is False
    assert error_msg is not None
    assert "172.16" in error_msg or "SSRF" in error_msg or "blocked" in error_msg
    assert document is None


def test_ssrf_protection_blocks_169_254_network():
    """Test that SSRF protection blocks 169.254.x.x network (link-local)."""
    ingestion_service = IngestionService()

    # Test with 169.254.x.x URL (should be blocked)
    success, error_msg, document = ingestion_service.ingest_from_url("http://169.254.0.1:8080/internal.html")

    # Verify the ingestion was blocked
    assert success is False
    assert error_msg is not None
    assert "169.254" in error_msg or "SSRF" in error_msg or "blocked" in error_msg
    assert document is None


def test_public_url_ingestion_allowed():
    """Test that public URLs are allowed through SSRF protection."""
    ingestion_service = IngestionService()

    # Mock successful public URL ingestion
    with patch.object(URLContentExtractor, 'save_url_content_to_temp_file') as mock_save:
        with patch.object(TextExtractor, 'extract_from_html') as mock_extract:
            # Create a temporary file to simulate downloaded content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write("<html><body>Public content</body></html>")
                temp_file_path = temp_file.name

            mock_save.return_value = temp_file_path
            mock_extract.return_value = "Public content"

            # Test with public URL (should be allowed)
            success, error_msg, document = ingestion_service.ingest_from_url("https://example.com/public.html")

            # Verify the ingestion was successful
            assert success is True
            assert error_msg is None
            assert document is not None
            assert document.processing_status == ProcessingStatus.COMPLETED

    # Clean up temporary file
    import os
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_url_ingestion_with_query_parameters():
    """Test URL ingestion with query parameters."""
    ingestion_service = IngestionService()

    # Mock the URL content fetching and text extraction
    with patch.object(URLContentExtractor, 'save_url_content_to_temp_file') as mock_save:
        with patch.object(TextExtractor, 'extract_from_html') as mock_extract:
            # Create a temporary file to simulate downloaded content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write("<html><body>Content with query params</body></html>")
                temp_file_path = temp_file.name

            mock_save.return_value = temp_file_path
            mock_extract.return_value = "Content with query params"

            # Test URL with query parameters
            success, error_msg, document = ingestion_service.ingest_from_url("https://example.com/page?param=value&other=test")

            # Verify the ingestion was successful
            assert success is True
            assert error_msg is None
            assert document is not None
            assert document.source_url == "https://example.com/page?param=value&other=test"
            assert document.processing_status == ProcessingStatus.COMPLETED

    # Clean up temporary file
    import os
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_url_ingestion_timeout_handling():
    """Test URL ingestion timeout handling."""
    ingestion_service = IngestionService()

    # Mock a timeout scenario
    with patch.object(URLContentExtractor, 'fetch_content_from_url') as mock_fetch:
        mock_fetch.side_effect = Exception("Request timeout after 30s")

        # Test the URL ingestion with timeout
        success, error_msg, document = ingestion_service.ingest_from_url("https://slow-example.com/content.html")

        # Verify the ingestion failed due to timeout
        assert success is False
        assert error_msg is not None
        assert "timeout" in error_msg.lower() or "request" in error_msg.lower()
        assert document is None


def test_url_ingestion_unreachable_host():
    """Test URL ingestion with unreachable host."""
    ingestion_service = IngestionService()

    # Mock an unreachable host scenario
    with patch.object(URLContentExtractor, 'fetch_content_from_url') as mock_fetch:
        mock_fetch.side_effect = Exception("Failed to connect to host")

        # Test the URL ingestion with unreachable host
        success, error_msg, document = ingestion_service.ingest_from_url("https://nonexistent-host-12345.com/content.html")

        # Verify the ingestion failed due to unreachable host
        assert success is False
        assert error_msg is not None
        assert "connect" in error_msg.lower() or "host" in error_msg.lower() or "failed" in error_msg.lower()
        assert document is None


def test_url_ingestion_with_malformed_content():
    """Test URL ingestion with malformed content."""
    ingestion_service = IngestionService()

    # Mock the URL content fetching with malformed content
    with patch.object(URLContentExtractor, 'save_url_content_to_temp_file') as mock_save:
        with patch.object(TextExtractor, 'extract_from_html') as mock_extract:
            # Create a temporary file with malformed content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write("<html><body><div><p>Unclosed tags and malformed content")
                temp_file_path = temp_file.name

            mock_save.return_value = temp_file_path
            mock_extract.return_value = "Unclosed tags and malformed content"  # Should still work

            # Test the URL ingestion
            success, error_msg, document = ingestion_service.ingest_from_url("https://example.com/malformed.html")

            # Verify the ingestion was successful despite malformed content
            assert success is True
            assert error_msg is None
            assert document is not None
            assert document.processing_status == ProcessingStatus.COMPLETED

    # Clean up temporary file
    import os
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


def test_url_ingestion_multiple_redirects():
    """Test URL ingestion with multiple redirects."""
    ingestion_service = IngestionService()

    # Mock the URL content fetching with redirect handling
    with patch.object(URLContentExtractor, 'save_url_content_to_temp_file') as mock_save:
        with patch.object(TextExtractor, 'extract_from_html') as mock_extract:
            # Create a temporary file to simulate downloaded content after redirects
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as temp_file:
                temp_file.write("<html><body>Content after multiple redirects</body></html>")
                temp_file_path = temp_file.name

            mock_save.return_value = temp_file_path
            mock_extract.return_value = "Content after multiple redirects"

            # Test the URL ingestion with multiple redirects
            success, error_msg, document = ingestion_service.ingest_from_url("https://example.com/initial-redirect")

            # Verify the ingestion was successful
            assert success is True
            assert error_msg is None
            assert document is not None
            assert document.processing_status == ProcessingStatus.COMPLETED
            assert document.source_url == "https://example.com/initial-redirect"

    # Clean up temporary file
    import os
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


if __name__ == "__main__":
    pytest.main([__file__])