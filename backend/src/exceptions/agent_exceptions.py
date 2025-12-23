from typing import Optional
from fastapi import HTTPException, status


class AgentBaseException(Exception):
    """
    Base exception class for agent-related errors.
    """
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class RetrievalException(AgentBaseException):
    """
    Exception raised when there are issues with document retrieval.
    """
    pass


class AgentProcessingException(AgentBaseException):
    """
    Exception raised when there are issues with agent processing.
    """
    pass


class InvalidQueryException(AgentBaseException):
    """
    Exception raised when the query is invalid.
    """
    pass


class ConfigurationException(AgentBaseException):
    """
    Exception raised when there are configuration issues.
    """
    pass


def handle_retrieval_error(error: Exception, query: str = "") -> HTTPException:
    """
    Handle retrieval errors and convert them to appropriate HTTP exceptions.
    """
    error_msg = f"Error during retrieval: {str(error)}"
    if query:
        error_msg += f" for query: {query[:50]}..."

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error_msg
    )


def handle_agent_error(error: Exception, query: str = "") -> HTTPException:
    """
    Handle agent processing errors and convert them to appropriate HTTP exceptions.
    """
    error_msg = f"Error during agent processing: {str(error)}"
    if query:
        error_msg += f" for query: {query[:50]}..."

    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=error_msg
    )


def handle_invalid_query_error(error: Exception) -> HTTPException:
    """
    Handle invalid query errors and convert them to appropriate HTTP exceptions.
    """
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Invalid query: {str(error)}"
    )


def handle_configuration_error(error: Exception) -> HTTPException:
    """
    Handle configuration errors and convert them to appropriate HTTP exceptions.
    """
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Configuration error: {str(error)}"
    )


# Custom HTTP exceptions for specific use cases
class QdrantConnectionError(AgentBaseException):
    """
    Exception raised when unable to connect to Qdrant.
    """
    pass


class OpenAIServiceError(AgentBaseException):
    """
    Exception raised when there are issues with the OpenAI service.
    """
    pass


def handle_qdrant_connection_error(error: Exception) -> HTTPException:
    """
    Handle Qdrant connection errors.
    """
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"Unable to connect to Qdrant: {str(error)}"
    )


def handle_openai_service_error(error: Exception) -> HTTPException:
    """
    Handle OpenAI service errors.
    """
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"OpenAI service error: {str(error)}"
    )