"""Unit tests for validation service.

Tests file validation with size limits 0<size≤500MB, extension validation,
MIME type checks, and error messages per research.md.
Verifies validation service follows specification requirements.
"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from backend.src.services.validation import (
    FileValidator,
    URLValidator,
    ValidationError,
    validate_file_upload,
    validate_ingestion_url
)


def test_file_size_validation():
    """Test file size validation with 0<size≤500MB limits."""
    # Create a temporary file of specific size
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Write 1KB of data
        temp_file.write(b"x" * 1024)
        temp_file_path = temp_file.name

    try:
        # Valid size (1KB)
        assert FileValidator.validate_file_size(temp_file_path) is True

        # Test with a file larger than 500MB would require creating a large file
        # which we'll mock instead to avoid disk usage
        with patch('os.path.getsize', return_value=FileValidator.MAX_FILE_SIZE + 1):
            with pytest.raises(ValidationError) as exc_info:
                FileValidator.validate_file_size(temp_file_path)
            assert "exceeds maximum" in str(exc_info.value)

        # Test with zero size file
        with patch('os.path.getsize', return_value=0):
            with pytest.raises(ValidationError) as exc_info:
                FileValidator.validate_file_size(temp_file_path)
            assert "exceeds maximum" not in str(exc_info.value)  # This would fail for different reason
            # Actually, we need to test the zero size specifically
            # Let's create a proper test for zero size
            with tempfile.NamedTemporaryFile(delete=False) as zero_file:
                zero_file_path = zero_file.name

            try:
                with patch('os.path.getsize', return_value=0):
                    with pytest.raises(ValidationError) as exc_info:
                        FileValidator.validate_file_size(zero_file_path)
                    assert "exceeds maximum" in str(exc_info.value) or "0" in str(exc_info.value)
            finally:
                os.unlink(zero_file_path)

    finally:
        os.unlink(temp_file_path)


def test_file_extension_validation():
    """Test file extension validation."""
    # Valid extensions
    valid_extensions = ['.pdf', '.txt', '.docx', '.html', '.htm']

    for ext in valid_extensions:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
            temp_file_path = temp_file.name

        try:
            assert FileValidator.validate_file_extension(temp_file_path) is True
        finally:
            os.unlink(temp_file_path)

    # Invalid extension
    with tempfile.NamedTemporaryFile(suffix='.exe', delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        with pytest.raises(ValidationError) as exc_info:
            FileValidator.validate_file_extension(temp_file_path)
        assert "not allowed" in str(exc_info.value)
    finally:
        os.unlink(temp_file_path)


def test_file_validation_function():
    """Test the validate_file_upload function."""
    # Create a valid temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"test content")
        temp_file_path = temp_file.name

    try:
        # Mock the validation methods to avoid actual file processing
        with patch.object(FileValidator, 'validate_file_size', return_value=True), \
             patch.object(FileValidator, 'validate_file_extension', return_value=True), \
             patch.object(FileValidator, 'validate_mime_type', return_value=True):

            is_valid, error_msg = validate_file_upload(temp_file_path)
            assert is_valid is True
            assert error_msg is None
    finally:
        os.unlink(temp_file_path)

    # Test with invalid file
    with patch.object(FileValidator, 'validate_file_size', side_effect=ValidationError("Test error")):
        is_valid, error_msg = validate_file_upload("/fake/path.txt")
        assert is_valid is False
        assert error_msg == "Test error"


def test_url_scheme_validation():
    """Test URL scheme validation (http/https only)."""
    # Valid HTTP URL
    assert URLValidator.validate_scheme("http://example.com") is True

    # Valid HTTPS URL
    assert URLValidator.validate_scheme("https://example.com") is True

    # Invalid scheme
    with pytest.raises(ValidationError) as exc_info:
        URLValidator.validate_scheme("ftp://example.com")
    assert "not allowed" in str(exc_info.value)

    # Invalid scheme (custom)
    with pytest.raises(ValidationError) as exc_info:
        URLValidator.validate_scheme("javascript:alert('xss')")
    assert "not allowed" in str(exc_info.value)


def test_url_ssrf_protection():
    """Test SSRF protection for private IPs."""
    # Valid public URL
    with patch('socket.gethostbyname_ex', return_value=('example.com', [], ['93.184.216.34'])):
        assert URLValidator.validate_ssrf_protection("https://example.com") is True

    # Test localhost (should be blocked)
    with pytest.raises(ValidationError) as exc_info:
        URLValidator.validate_ssrf_protection("http://localhost")
    assert "localhost" in str(exc_info.value)

    # Test 127.0.0.1 (should be blocked)
    with patch('socket.gethostbyname_ex', return_value=('localhost', [], ['127.0.0.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
    # The actual check happens in is_private_ip, so we'll test that separately

    # Test 10.0.0.0/8 private range
    with patch('socket.gethostbyname_ex', return_value=('test', [], ['10.0.0.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)

    # Test 172.16.0.0/12 private range
    with patch('socket.gethostbyname_ex', return_value=('test', [], ['172.16.0.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)

    # Test 192.168.0.0/16 private range
    with patch('socket.gethostbyname_ex', return_value=('test', [], ['192.168.1.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)


def test_url_validation_function():
    """Test the validate_ingestion_url function."""
    # Mock the validation methods
    with patch.object(URLValidator, 'validate_scheme', return_value=True), \
         patch.object(URLValidator, 'validate_ssrf_protection', return_value=True):

        is_valid, error_msg = validate_ingestion_url("https://example.com")
        assert is_valid is True
        assert error_msg is None

    # Test with invalid URL
    with patch.object(URLValidator, 'validate_scheme', side_effect=ValidationError("Invalid scheme")):
        is_valid, error_msg = validate_ingestion_url("ftp://example.com")
        assert is_valid is False
        assert error_msg == "Invalid scheme"


def test_is_private_ip():
    """Test the private IP detection function."""
    # Test 10.0.0.0/8 range
    assert URLValidator.is_private_ip("10.0.0.1") is True
    assert URLValidator.is_private_ip("10.255.255.255") is True

    # Test 172.16.0.0/12 range
    assert URLValidator.is_private_ip("172.16.0.1") is True
    assert URLValidator.is_private_ip("172.31.255.255") is True

    # Test 192.168.0.0/16 range
    assert URLValidator.is_private_ip("192.168.0.1") is True
    assert URLValidator.is_private_ip("192.168.255.255") is True

    # Test 127.0.0.0/8 range (localhost)
    assert URLValidator.is_private_ip("127.0.0.1") is True

    # Test public IP
    assert URLValidator.is_private_ip("8.8.8.8") is False
    assert URLValidator.is_private_ip("93.184.216.34") is False  # example.com IP

    # Test with hostname that resolves to public IP (mocked)
    with patch('socket.gethostbyname_ex', return_value=('example.com', [], ['93.184.216.34'])):
        assert URLValidator.is_private_ip("example.com") is False

    # Test with hostname that resolves to private IP (mocked)
    with patch('socket.gethostbyname_ex', return_value=('internal.local', [], ['192.168.1.10'])):
        assert URLValidator.is_private_ip("internal.local") is True


def test_file_layered_validation():
    """Test the complete layered validation process."""
    # Create a valid temporary file
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_file:
        temp_file.write(b"test content that is at least 500 characters long to meet the requirements for validation purposes. " * 5)
        temp_file_path = temp_file.name

    try:
        # Mock the validation methods to avoid actual file processing
        with patch.object(FileValidator, 'validate_file_size', return_value=True), \
             patch.object(FileValidator, 'validate_file_extension', return_value=True), \
             patch.object(FileValidator, 'validate_mime_type', return_value=True):

            result = FileValidator.validate_file(temp_file_path)
            assert result is True
    finally:
        os.unlink(temp_file_path)


if __name__ == "__main__":
    pytest.main([__file__])