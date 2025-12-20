from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Any, Optional
from ..config.settings import settings


def get_qdrant_client():
    """
    Initialize and return Qdrant client with configured settings.
    """
    if settings.qdrant_api_key:
        client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False  # Using HTTP for better compatibility
        )
    else:
        client = QdrantClient(url=settings.qdrant_url)

    return client


# Initialize the client
qdrant_client = get_qdrant_client()


def get_collection_info(collection_name: str) -> Dict[str, Any]:
    """
    Get information about a specific collection.
    """
    return qdrant_client.get_collection(collection_name=collection_name)


def check_collection_exists(collection_name: str) -> bool:
    """
    Check if a collection exists in Qdrant.
    """
    try:
        qdrant_client.get_collection(collection_name=collection_name)
        return True
    except Exception:
        return False