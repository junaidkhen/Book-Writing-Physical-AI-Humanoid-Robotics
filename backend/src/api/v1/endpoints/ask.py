from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import time
import uuid

from src.schemas.query_schemas import QueryRequest
from src.schemas.response_schemas import QueryResponse
from src.agents.rag_agent import rag_agent
from src.utils.metrics import metrics_tracker
from src.utils.logging import logger
from src.exceptions.agent_exceptions import handle_agent_error, handle_invalid_query_error

router = APIRouter()


@router.post("/ask", response_model=QueryResponse)
async def ask_endpoint(request: Request, query_request: QueryRequest):
    """
    Process a query and return a grounded answer with citations.
    """
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Add request ID to logger context if possible
    logger.info(
        f"Processing ask request",
        extra={"request_id": request_id, "query_length": len(query_request.query)}
    )

    try:
        # Validate input parameters
        if not query_request.query or len(query_request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        if query_request.top_k and (query_request.top_k < 1 or query_request.top_k > 20):
            raise HTTPException(status_code=400, detail="top_k must be between 1 and 20")

        if query_request.temperature and (query_request.temperature < 0.0 or query_request.temperature > 0.2):
            raise HTTPException(status_code=400, detail="temperature must be between 0.0 and 0.2")

        # Process the query using the RAG agent
        answer, citations, reasoning, metadata = await rag_agent.query(
            query=query_request.query,
            top_k=query_request.top_k or 5,
            temperature=query_request.temperature or 0.1
        )

        # Record metrics
        total_time = (time.time() - start_time) * 1000
        metrics_tracker.record_query(
            retrieval_time=metadata.retrieval_time,
            agent_time=metadata.agent_time,
            total_time=total_time,
            tokens_used=metadata.token_usage.total_tokens
        )

        # Create the response
        response = QueryResponse(
            answer=answer,
            citations=citations,
            reasoning=reasoning,
            metadata=metadata
        )

        logger.info(
            f"Successfully processed ask request",
            extra={"request_id": request_id, "response_length": len(answer), "total_time_ms": total_time}
        )

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Record error in metrics
        metrics_tracker.record_error()

        logger.error(
            f"Error in ask endpoint: {str(e)}",
            extra={"request_id": request_id}
        )

        # Handle the error appropriately
        raise handle_agent_error(e, query_request.query)