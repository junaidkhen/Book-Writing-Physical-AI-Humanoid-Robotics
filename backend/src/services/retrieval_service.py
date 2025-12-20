from typing import List, Dict, Any, Tuple
from qdrant_client.http import models
from ..clients.qdrant_client import qdrant_client
from ..config.settings import settings
from ..schemas.response_schemas import RetrievedChunk, ChunkMetadata
from ..utils.logging import logger
import time
import asyncio


async def retrieve_chunks(query: str, top_k: int = 5) -> Tuple[List[RetrievedChunk], float]:
    """
    Retrieve top-k relevant chunks from Qdrant based on the query.

    Args:
        query: The user's search query
        top_k: Number of chunks to retrieve (default: 5)

    Returns:
        Tuple of (list of retrieved chunks, retrieval time in milliseconds)
    """
    start_time = time.time()

    try:
        # Use Qdrant's query_points API for semantic search
        search_results = qdrant_client.query_points(
            collection_name=settings.qdrant_collection_name,
            query_text=query,  # Using text-based search
            limit=top_k,
            with_payload=True,
            with_vectors=False
        ).points

        # Convert Qdrant results to our RetrievedChunk format
        retrieved_chunks = []
        for result in search_results:
            # Extract payload data
            payload = result.payload
            metadata = ChunkMetadata(
                chapter=payload.get('chapter', 'Unknown'),
                section=payload.get('section', 'Unknown'),
                page=payload.get('page'),
                source_document=payload.get('source_document', 'Unknown')
            )

            # Create RetrievedChunk object
            chunk = RetrievedChunk(
                chunk_id=str(result.id),
                content=payload.get('content', ''),
                metadata=metadata,
                score=result.score
            )
            retrieved_chunks.append(chunk)

        retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks for query: {query[:50]}...")

        return retrieved_chunks, retrieval_time

    except Exception as e:
        retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.error(f"Error during retrieval: {str(e)}")
        raise e


async def retrieve_chunks_with_embeddings(query: str, top_k: int = 5) -> Tuple[List[RetrievedChunk], float]:
    """
    Alternative retrieval method using embeddings (if needed).
    This method generates embeddings for the query and searches using vector similarity.
    """
    start_time = time.time()

    try:
        # This would use Cohere or OpenAI to generate embeddings
        # For now, we'll use the text-based search approach
        return await retrieve_chunks(query, top_k)
    except Exception as e:
        retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.error(f"Error during embedding-based retrieval: {str(e)}")
        raise e


def validate_retrieval_parameters(query: str, top_k: int) -> None:
    """
    Validate retrieval parameters before processing.
    """
    if not query or len(query.strip()) == 0:
        raise ValueError("Query cannot be empty")

    if top_k < 1 or top_k > 20:
        raise ValueError("top_k must be between 1 and 20")