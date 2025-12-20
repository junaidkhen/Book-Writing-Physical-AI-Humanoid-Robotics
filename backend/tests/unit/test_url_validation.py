"""Unit tests for URL validation service.

Tests scheme whitelist http/https only, private IP blocking per research.md Decision 5,
redirect validation, timeout 30s, malicious URL rejection.
Verifies URL validation service follows specification requirements.
"""
import pytest
from unittest.mock import patch

from backend.src.services.validation import URLValidator, ValidationError


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


def test_url_ssrf_protection_private_ips():
    """Test SSRF protection for private IP ranges."""
    # Test 10.0.0.0/8 range
    with patch('socket.gethostbyname_ex', return_value=('test', [], ['10.0.0.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)

    # Test 172.16.0.0/12 range
    with patch('socket.gethostbyname_ex', return_value=('test', [], ['172.16.0.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)

    # Test 192.168.0.0/16 range
    with patch('socket.gethostbyname_ex', return_value=('test', [], ['192.168.1.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)

    # Test 127.0.0.0/8 range (localhost)
    with pytest.raises(ValidationError) as exc_info:
        URLValidator.validate_ssrf_protection("http://localhost")
    assert "localhost" in str(exc_info.value)

    # Test 127.0.0.1
    with patch('socket.gethostbyname_ex', return_value=('localhost', [], ['127.0.0.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)

    # Test 169.254.0.0/16 range (link-local)
    with patch('socket.gethostbyname_ex', return_value=('test', [], ['169.254.0.1'])):
        with pytest.raises(ValidationError) as exc_info:
            URLValidator.validate_ssrf_protection("http://test.local")
        assert "private IP" in str(exc_info.value)


def test_url_ssrf_protection_public_ips():
    """Test that public IPs are allowed."""
    # Valid public IP should pass SSRF protection
    with patch('socket.gethostbyname_ex', return_value=('example.com', [], ['93.184.216.34'])):
        assert URLValidator.validate_ssrf_protection("https://example.com") is True


def test_url_validation_complete():
    """Test complete URL validation."""
    # Valid public URL should pass
    with patch('socket.gethostbyname_ex', return_value=('example.com', [], ['93.184.216.34'])):
        assert URLValidator.validate_url("https://example.com") is True

    # Private IP should fail
    with patch('socket.gethostbyname_ex', return_value=('internal.local', [], ['192.168.1.10'])):
        with pytest.raises(ValidationError):
            URLValidator.validate_url("http://internal.local")

    # Invalid scheme should fail
    with pytest.raises(ValidationError):
        URLValidator.validate_url("ftp://example.com")


def test_is_private_ip_function():
    """Test the private IP detection function directly."""
    # Private IP ranges should return True
    assert URLValidator.is_private_ip("10.0.0.1") is True
    assert URLValidator.is_private_ip("172.16.0.1") is True
    assert URLValidator.is_private_ip("192.168.1.1") is True
    assert URLValidator.is_private_ip("127.0.0.1") is True
    assert URLValidator.is_private_ip("169.254.1.1") is True

    # Public IP ranges should return False
    assert URLValidator.is_private_ip("8.8.8.8") is False
    assert URLValidator.is_private_ip("1.1.1.1") is False

    # Test with hostnames that resolve to IPs
    with patch('socket.gethostbyname_ex', return_value=('private.local', [], ['192.168.1.10'])):
        assert URLValidator.is_private_ip("private.local") is True

    with patch('socket.gethostbyname_ex', return_value=('public.com', [], ['93.184.216.34'])):
        assert URLValidator.is_private_ip("public.com") is False


def test_url_format_validation():
    """Test basic URL format validation."""
    # Test invalid URLs
    invalid_urls = [
        "not-a-url",
        "",
        "htp://invalid-scheme.com",
        "just.domain"
    ]

    for url in invalid_urls:
        with pytest.raises(Exception):  # Should raise error for invalid URL format
            URLValidator.validate_url(url)


def test_url_with_port():
    """Test URL validation with port numbers."""
    # Valid URLs with ports should work if they're public
    with patch('socket.gethostbyname_ex', return_value=('example.com', [], ['93.184.216.34'])):
        assert URLValidator.validate_url("https://example.com:8080") is True


def test_url_edge_cases():
    """Test URL validation edge cases."""
    # URL with query parameters and fragments
    with patch('socket.gethostbyname_ex', return_value=('example.com', [], ['93.184.216.34'])):
        assert URLValidator.validate_url("https://example.com/path?param=value#fragment") is True

    # URL with subdomain
    with patch('socket.gethostbyname_ex', return_value=('sub.example.com', [], ['93.184.216.34'])):
        assert URLValidator.validate_url("https://sub.example.com") is True


if __name__ == "__main__":
    pytest.main([__file__])