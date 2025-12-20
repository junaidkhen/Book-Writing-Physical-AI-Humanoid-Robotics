from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import time
import uuid

from backend.src.schemas.query_schemas import RetrievalRequest
from backend.src.schemas.response_schemas import RetrievalResponse, RetrievalMetadata
from backend.src.services.retrieval_service import retrieve_chunks, validate_retrieval_parameters
from backend.src.utils.metrics import metrics_tracker
from backend.src.utils.logging import logger
from backend.src.exceptions.agent_exceptions import handle_retrieval_error

router = APIRouter()


@router.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_endpoint(request: RetrievalRequest):
    """
    Retrieve raw book chunks relevant to a query without agent synthesis.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    logger.info(
        f"Processing retrieve request",
        extra={"request_id": request_id, "query_length": len(request.query)}
    )

    try:
        # Validate input parameters
        validate_retrieval_parameters(request.query, request.top_k or 5)

        # Retrieve chunks using the retrieval service
        chunks, retrieval_time = await retrieve_chunks(
            query=request.query,
            top_k=request.top_k or 5
        )

        # Calculate total processing time
        total_time = (time.time() - start_time) * 1000

        # Create retrieval metadata
        retrieval_metadata = RetrievalMetadata(
            query=request.query,
            chunks_returned=len(chunks),
            retrieval_time=retrieval_time,
            similarity_threshold=0.0  # Default threshold
        )

        # Create the response
        response = RetrievalResponse(
            chunks=chunks,
            metadata=retrieval_metadata
        )

        # Record metrics
        metrics_tracker.record_query(
            retrieval_time=retrieval_time,
            agent_time=0,  # No agent processing in this endpoint
            total_time=total_time,
            tokens_used=0  # No tokens used in retrieval-only endpoint
        )

        logger.info(
            f"Successfully processed retrieve request",
            extra={"request_id": request_id, "chunks_returned": len(chunks), "total_time_ms": total_time}
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Record error in metrics
        metrics_tracker.record_error()

        logger.error(
            f"Error in retrieve endpoint: {str(e)}",
            extra={"request_id": request_id}
        )

        # Handle the error appropriately
        raise handle_retrieval_error(e, request.query)