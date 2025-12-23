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
        # Import Cohere client for generating query embeddings
        import cohere
        from dotenv import load_dotenv
        import os
        from pathlib import Path

        # Load environment variables from backend/.env
        backend_dir = Path(__file__).parent.parent.parent
        env_path = backend_dir / ".env"
        load_dotenv(dotenv_path=env_path)
        cohere_api_key = os.getenv("COHERE_API_KEY")

        if not cohere_api_key:
            logger.error("COHERE_API_KEY not found in environment")
            retrieval_time = (time.time() - start_time) * 1000
            return [], retrieval_time

        # Generate embedding for the query
        cohere_client = cohere.Client(cohere_api_key)
        response = cohere_client.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        )
        query_embedding = response.embeddings[0]

        logger.info(f"Generated query embedding (dimension: {len(query_embedding)})")

        # Search Qdrant using the query embedding
        search_results = qdrant_client.search(
            collection_name=settings.qdrant_collection_name,
            query_vector=query_embedding,
            limit=top_k
        )

        logger.info(f"Found {len(search_results)} results from Qdrant")

        # Convert Qdrant results to our RetrievedChunk format
        retrieved_chunks = []
        for result in search_results:
            # Extract payload data
            payload = result.payload

            # Handle different payload structures
            # New structure: text_content + document_metadata
            # Old structure: content + direct chapter/section/page
            content = payload.get('text_content') or payload.get('content', '')
            doc_metadata = payload.get('document_metadata', {})

            # Extract chapter and section from source_url if available
            source_url = doc_metadata.get('source_url', '')
            chapter = 'Unknown'
            section = 'Unknown'

            if source_url:
                # Parse URL like: /docs/module-2/week-07-hri
                parts = source_url.split('/')
                if len(parts) >= 3:
                    # Extract module (e.g., 'module-2')
                    chapter = parts[-2] if 'module' in parts[-2] else parts[-2]
                    # Extract section (e.g., 'week-07-hri')
                    section = parts[-1]

            # Fallback to direct fields if they exist
            chapter = doc_metadata.get('chapter') or payload.get('chapter', chapter)
            section = doc_metadata.get('section') or payload.get('section', section)

            metadata = ChunkMetadata(
                chapter=chapter,
                section=section,
                page=doc_metadata.get('page') or payload.get('page'),
                source_document=source_url or doc_metadata.get('filename', 'Unknown')
            )

            # Create RetrievedChunk object
            chunk = RetrievedChunk(
                chunk_id=str(result.id),
                content=content,
                metadata=metadata,
                score=result.score
            )
            retrieved_chunks.append(chunk)

        retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks for query: {query[:50]}... in {retrieval_time:.2f}ms")

        return retrieved_chunks, retrieval_time

    except Exception as e:
        retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        logger.error(f"Error during retrieval: {str(e)}")
        # Return empty list instead of raising exception
        return [], retrieval_time


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