"""Structured logging configuration with JSON format and request ID tracking

Per Constitution Principle VI: Observability & Logging
- JSON format for structured logging
- Request ID tracking for distributed tracing
- Configurable log levels
"""

import logging
import sys
import uuid
from datetime import datetime
from typing import Any, Dict
import json


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string

        Args:
            record: Log record to format

        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add request ID if available (set by middleware)
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configure structured logging for the application

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured root logger
    """
    # Get root logger
    logger = logging.getLogger()

    # Clear existing handlers
    logger.handlers.clear()

    # Set log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)

    # Create console handler with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(JSONFormatter())

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def log_with_request_id(
    logger: logging.Logger,
    level: int,
    message: str,
    request_id: str | None = None,
    **extra_fields: Any,
) -> None:
    """Log a message with request ID and extra fields

    Args:
        logger: Logger instance
        level: Log level (logging.INFO, logging.ERROR, etc.)
        message: Log message
        request_id: Optional request ID for tracing
        **extra_fields: Additional fields to include in log
    """
    extra = {"extra_fields": extra_fields}
    if request_id:
        extra["request_id"] = request_id

    logger.log(level, message, extra=extra)


def generate_request_id() -> str:
    """Generate a unique request ID for tracing

    Returns:
        UUID string for request tracking
    """
    return str(uuid.uuid4())
