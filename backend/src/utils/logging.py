import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter that adds additional fields to log entries.
    """
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)

        # Add timestamp in ISO format
        log_record['timestamp'] = datetime.utcnow().isoformat()

        # Add severity level (for cloud logging compatibility)
        log_record['severity'] = record.levelname

        # Add service name
        log_record['service'] = 'rag-agent-service'

        # Add request ID if available in the logger
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id


def setup_structured_logging(level: str = "INFO") -> logging.Logger:
    """
    Set up structured JSON logging for the application.
    """
    logger = logging.getLogger("rag-agent-service")
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Create and set the custom JSON formatter
    formatter = CustomJsonFormatter(
        '%(timestamp)s %(severity)s %(name)s %(message)s %(module)s %(funcName)s %(lineno)d',
        rename_fields={'levelname': 'severity', 'name': 'logger'}
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance with structured JSON logging.
    """
    logger_name = f"rag-agent-service.{name}" if name else "rag-agent-service"
    return logging.getLogger(logger_name)


# Global logger instance
logger = setup_structured_logging()