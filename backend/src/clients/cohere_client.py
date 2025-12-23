import cohere
from typing import Optional
from ..config.settings import settings


def get_cohere_client():
    """
    Initialize and return Cohere client with configured settings.
    If no API key is provided, returns None.
    """
    if settings.cohere_api_key:
        client = cohere.Client(api_key=settings.cohere_api_key)
        return client
    else:
        return None


# Initialize the client
cohere_client = get_cohere_client()