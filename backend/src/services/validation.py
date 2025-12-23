"""File validation service for the document ingestion system.

Implements layered validation: size → extension → MIME type per research.md Decision 6.
Handles file format validation, size limits, and URL validation with SSRF protection.
"""
import os
import re
from typing import Optional, Tuple
from urllib.parse import urlparse
import mimetypes
import socket
import ipaddress

import magic  # python-magic library for MIME type detection

from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class FileValidator:
    """File validation service with layered validation approach."""

    # Allowed file extensions and their MIME types
    ALLOWED_EXTENSIONS = {'.pdf', '.txt', '.docx', '.html', '.htm'}
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'text/plain',
        'text/html',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    }

    # Max file size: 500MB (524288000 bytes)
    MAX_FILE_SIZE = 524288000

    @classmethod
    def validate_file_size(cls, file_path: str) -> bool:
        """Validate file size is within limits.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file size is valid, raises ValidationError otherwise

        Per research.md Decision 6: Size validation first layer
        """
        file_size = os.path.getsize(file_path)
        if file_size <= 0 or file_size > cls.MAX_FILE_SIZE:
            raise ValidationError(
                f"File size {file_size} bytes exceeds maximum of {cls.MAX_FILE_SIZE} bytes "
                f"({cls.MAX_FILE_SIZE / (1024*1024):.1f}MB)"
            )
        logger.info(f"File size validation passed: {file_size} bytes")
        return True

    @classmethod
    def validate_file_extension(cls, file_path: str) -> bool:
        """Validate file extension is allowed.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if extension is valid, raises ValidationError otherwise
        """
        _, ext = os.path.splitext(file_path.lower())
        if ext not in cls.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"File extension '{ext}' not allowed. "
                f"Allowed extensions: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )
        logger.info(f"File extension validation passed: {ext}")
        return True

    @classmethod
    def validate_mime_type(cls, file_path: str) -> bool:
        """Validate actual MIME type matches expected type.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if MIME type is valid, raises ValidationError otherwise

        Uses python-magic for accurate MIME detection per research.md
        """
        # Use python-magic for accurate MIME type detection
        mime_type = magic.from_file(file_path, mime=True)

        if mime_type not in cls.ALLOWED_MIME_TYPES:
            # Also check with mimetypes library as backup
            _, ext = os.path.splitext(file_path.lower())
            backup_mime = mimetypes.guess_type(file_path)[0]

            if backup_mime not in cls.ALLOWED_MIME_TYPES:
                raise ValidationError(
                    f"MIME type '{mime_type}' not allowed. "
                    f"Detected: {mime_type}, expected one of: {', '.join(cls.ALLOWED_MIME_TYPES)}"
                )

        logger.info(f"MIME type validation passed: {mime_type}")
        return True

    @classmethod
    def validate_file(cls, file_path: str) -> bool:
        """Validate file using layered approach: size → extension → MIME type.

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file passes all validations, raises ValidationError otherwise

        Per research.md Decision 6: Layered validation approach
        """
        logger.info(f"Starting validation for file: {file_path}")

        # Layer 1: Size validation
        cls.validate_file_size(file_path)

        # Layer 2: Extension validation
        cls.validate_file_extension(file_path)

        # Layer 3: MIME type validation
        cls.validate_mime_type(file_path)

        logger.info(f"File validation passed: {file_path}")
        return True


class URLValidator:
    """URL validation service with SSRF protection per research.md Decision 5."""

    # Allowed URL schemes
    ALLOWED_SCHEMES = {'http', 'https'}

    # Private IP ranges to block (SSRF protection)
    PRIVATE_IP_RANGES = [
        ipaddress.IPv4Network('10.0.0.0/8'),      # 10.0.0.0 - 10.255.255.255
        ipaddress.IPv4Network('172.16.0.0/12'),   # 172.16.0.0 - 172.31.255.255
        ipaddress.IPv4Network('192.168.0.0/16'),  # 192.168.0.0 - 192.168.255.255
        ipaddress.IPv4Network('127.0.0.0/8'),     # 127.0.0.0 - 127.255.255.255 (localhost)
        ipaddress.IPv4Network('169.254.0.0/16'),  # 169.254.0.0 - 169.254.255.255 (link-local)
    ]

    @classmethod
    def validate_scheme(cls, url: str) -> bool:
        """Validate URL scheme is allowed (http/https only).

        Args:
            url: URL to validate

        Returns:
            True if scheme is valid, raises ValidationError otherwise
        """
        parsed = urlparse(url)
        if parsed.scheme not in cls.ALLOWED_SCHEMES:
            raise ValidationError(
                f"URL scheme '{parsed.scheme}' not allowed. "
                f"Only schemes allowed: {', '.join(cls.ALLOWED_SCHEMES)}"
            )
        logger.info(f"URL scheme validation passed: {parsed.scheme}")
        return True

    @classmethod
    def is_private_ip(cls, hostname: str) -> bool:
        """Check if hostname resolves to a private IP address.

        Args:
            hostname: Hostname to check

        Returns:
            True if hostname resolves to private IP, False otherwise
        """
        try:
            # Get IP address for hostname
            ip_addresses = socket.gethostbyname_ex(hostname)[2]

            for ip_str in ip_addresses:
                ip = ipaddress.IPv4Address(ip_str)
                for private_range in cls.PRIVATE_IP_RANGES:
                    if ip in private_range:
                        return True
        except (socket.gaierror, ValueError, ipaddress.AddressValueError):
            # If hostname can't be resolved or IP is invalid, return False
            # (validation will catch other issues)
            pass

        return False

    @classmethod
    def validate_ssrf_protection(cls, url: str) -> bool:
        """Validate URL does not point to private IPs (SSRF protection).

        Args:
            url: URL to validate

        Returns:
            True if URL passes SSRF checks, raises ValidationError otherwise
        """
        parsed = urlparse(url)
        hostname = parsed.hostname

        if not hostname:
            raise ValidationError(f"Invalid URL: {url} - no hostname found")

        # Check if hostname is localhost or private IP
        if hostname.lower() in ['localhost', 'localhost.']:
            raise ValidationError(f"URL points to localhost which is blocked for SSRF protection: {url}")

        # Check if hostname resolves to private IP
        if cls.is_private_ip(hostname):
            raise ValidationError(f"URL resolves to private IP which is blocked for SSRF protection: {url}")

        logger.info(f"SSRF protection validation passed: {url}")
        return True

    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL with SSRF protection.

        Args:
            url: URL to validate

        Returns:
            True if URL passes all validations, raises ValidationError otherwise
        """
        logger.info(f"Starting URL validation: {url}")

        # Validate URL format and scheme
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValidationError(f"Invalid URL format: {url}")

        # Validate scheme
        cls.validate_scheme(url)

        # SSRF protection
        cls.validate_ssrf_protection(url)

        logger.info(f"URL validation passed: {url}")
        return True


def validate_file_upload(file_path: str) -> Tuple[bool, Optional[str]]:
    """Validate file upload with comprehensive checks.

    Args:
        file_path: Path to uploaded file

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        FileValidator.validate_file(file_path)
        return True, None
    except ValidationError as e:
        logger.warning(f"File validation failed: {e}")
        return False, str(e)


def validate_ingestion_url(url: str) -> Tuple[bool, Optional[str]]:
    """Validate URL for ingestion with SSRF protection.

    Args:
        url: URL to validate for ingestion

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        URLValidator.validate_url(url)
        return True, None
    except ValidationError as e:
        logger.warning(f"URL validation failed: {e}")
        return False, str(e)