"""Storage service for Qdrant vector database and Cohere embeddings

Handles:
- Qdrant client initialization and collection management
- Cohere embedding generation
- Chunk storage and retrieval
- Document metadata denormalization per data-model.md
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import cohere

from ..utils.logging_config import get_logger

logger = get_logger(__name__)


class QdrantStorage:
    """Qdrant vector storage client with collection management"""

    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        collection_name: str = "documents",
    ):
        """Initialize Qdrant client

        Args:
            url: Qdrant instance URL
            api_key: Optional API key for authentication
            collection_name: Collection name for storing chunks

        Per research.md Decision 4: Use connection pooling and batch upserts
        """
        self.collection_name = collection_name
        self.client = QdrantClient(
            url=url,
            api_key=api_key,
            timeout=30,  # 30s timeout for requests
        )
        logger.info(f"Initialized Qdrant client for {url}")

    def create_collection(self, vector_size: int = 1024) -> None:
        """Create collection with vector configuration

        Args:
            vector_size: Embedding dimension (1024 for Cohere embed-english-v3.0)

        Per data-model.md: Cosine distance for text similarity
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]

            if self.collection_name in collection_names:
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            # Create collection with vector configuration
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,  # Standard for text embeddings
                ),
            )
            logger.info(f"Created collection '{self.collection_name}' with vector size {vector_size}")

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def upsert_chunks(
        self,
        chunks: List[Dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        """Batch upsert chunks to Qdrant

        Args:
            chunks: List of chunk dictionaries with fields from data-model.md
            batch_size: Number of points to upsert per batch (default 100)

        Returns:
            Number of chunks successfully upserted

        Per research.md Decision 4: Batch upserts for 10x better throughput
        """
        if not chunks:
            return 0

        points: List[PointStruct] = []
        for chunk in chunks:
            # Create Qdrant point with denormalized document metadata
            point = PointStruct(
                id=chunk.get("chunk_id", str(uuid.uuid4())),
                vector=chunk["embedding_vector"],
                payload={
                    # Chunk-specific fields
                    "document_id": chunk["document_id"],
                    "chunk_index": chunk["chunk_index"],
                    "text_content": chunk["text_content"],
                    "char_count": chunk["char_count"],
                    "start_position": chunk.get("start_position"),
                    "end_position": chunk.get("end_position"),
                    "embedding_model": chunk.get("embedding_model"),
                    "created_at": chunk.get("created_at", datetime.utcnow().isoformat()),
                    # Denormalized document metadata for single-query retrieval
                    "document_metadata": chunk.get("document_metadata", {}),
                },
            )
            points.append(point)

        # Batch upsert
        try:
            for i in range(0, len(points), batch_size):
                batch = points[i : i + batch_size]
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                )
                logger.info(f"Upserted batch {i // batch_size + 1}: {len(batch)} chunks")

            logger.info(f"Successfully upserted {len(points)} chunks")
            return len(points)

        except Exception as e:
            logger.error(f"Failed to upsert chunks: {e}")
            raise

    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single chunk by ID

        Args:
            chunk_id: Chunk UUID

        Returns:
            Chunk data or None if not found
        """
        try:
            point = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[chunk_id],
                with_vectors=True,
                with_payload=True,
            )

            if not point:
                return None

            return {
                "chunk_id": point[0].id,
                "embedding_vector": point[0].vector,
                **point[0].payload,
            }

        except Exception as e:
            logger.error(f"Failed to retrieve chunk {chunk_id}: {e}")
            return None

    def search_similar_chunks(
        self,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks using vector similarity

        Args:
            query_vector: Query embedding vector
            limit: Maximum number of results
            score_threshold: Minimum similarity score (0-1)

        Returns:
            List of similar chunks with scores
        """
        try:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
            )

            chunks = []
            for result in results:
                chunks.append({
                    "chunk_id": result.id,
                    "score": result.score,
                    "text_content": result.payload.get("text_content"),
                    "document_metadata": result.payload.get("document_metadata", {}),
                    **result.payload,
                })

            logger.info(f"Found {len(chunks)} similar chunks")
            return chunks

        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def delete_document_chunks(self, document_id: str) -> int:
        """Delete all chunks for a document

        Args:
            document_id: Document UUID

        Returns:
            Number of chunks deleted
        """
        try:
            # Delete by filter
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="document_id",
                                match=models.MatchValue(value=document_id),
                            )
                        ]
                    )
                ),
            )
            logger.info(f"Deleted chunks for document {document_id}")
            return 1  # Qdrant doesn't return delete count

        except Exception as e:
            logger.error(f"Failed to delete chunks for document {document_id}: {e}")
            raise


class CohereEmbeddings:
    """Cohere embedding generation client"""

    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        """Initialize Cohere client

        Args:
            api_key: Cohere API key
            model: Embedding model (default: embed-english-v3.0, 1024 dimensions)

        Per research.md: Use embed-english-v3.0 for 1024-dim embeddings
        """
        self.model = model
        self.client = cohere.Client(api_key)
        logger.info(f"Initialized Cohere client with model {model}")

    def embed_texts(
        self,
        texts: List[str],
        input_type: str = "search_document",
    ) -> List[List[float]]:
        """Generate embeddings for text chunks

        Args:
            texts: List of text chunks to embed
            input_type: Type of input (search_document, search_query, classification)

        Returns:
            List of embedding vectors (1024 dimensions each)

        Per data-model.md: Embedding dimension must be 1024
        """
        if not texts:
            return []

        try:
            response = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=input_type,
            )

            embeddings = response.embeddings
            logger.info(f"Generated {len(embeddings)} embeddings with dimension {len(embeddings[0])}")

            # Validate dimension
            if embeddings and len(embeddings[0]) != 1024:
                logger.warning(f"Expected 1024 dimensions, got {len(embeddings[0])}")

            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query

        Args:
            query: Query text

        Returns:
            Embedding vector (1024 dimensions)
        """
        embeddings = self.embed_texts([query], input_type="search_query")
        return embeddings[0] if embeddings else []


# Global client instances (initialized by FastAPI lifespan)
qdrant_client: Optional[QdrantStorage] = None
cohere_client: Optional[CohereEmbeddings] = None


def get_qdrant_client() -> QdrantStorage:
    """Get global Qdrant client instance

    Returns:
        QdrantStorage instance

    Raises:
        RuntimeError: If client not initialized
    """
    if qdrant_client is None:
        raise RuntimeError("Qdrant client not initialized. Call initialize_clients() first.")
    return qdrant_client


def get_cohere_client() -> CohereEmbeddings:
    """Get global Cohere client instance

    Returns:
        CohereEmbeddings instance

    Raises:
        RuntimeError: If client not initialized
    """
    if cohere_client is None:
        raise RuntimeError("Cohere client not initialized. Call initialize_clients() first.")
    return cohere_client


def initialize_clients(
    qdrant_url: str,
    qdrant_api_key: Optional[str],
    cohere_api_key: str,
) -> None:
    """Initialize global client instances

    Args:
        qdrant_url: Qdrant instance URL
        qdrant_api_key: Optional Qdrant API key
        cohere_api_key: Cohere API key

    Called during FastAPI app startup
    """
    global qdrant_client, cohere_client

    qdrant_client = QdrantStorage(url=qdrant_url, api_key=qdrant_api_key)
    qdrant_client.create_collection()  # Ensure collection exists

    cohere_client = CohereEmbeddings(api_key=cohere_api_key)

    logger.info("Initialized storage and embedding clients")


def shutdown_clients() -> None:
    """Shutdown global client instances

    Called during FastAPI app shutdown
    """
    global qdrant_client, cohere_client

    qdrant_client = None
    cohere_client = None

    logger.info("Shutdown storage and embedding clients")
