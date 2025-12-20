from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
from ..services.rag_agent import RAGAgent

router = APIRouter()

# Request models
class ChatRequest(BaseModel):
    query: str
    context: Optional[str] = None
    selected_text: Optional[str] = None
    stream: Optional[bool] = False

# Response models
class ChatResponse(BaseModel):
    response: str
    citations: Optional[List[Dict[str, Any]]] = []
    sources: Optional[List[str]] = []

class StreamChunk(BaseModel):
    type: str  # 'content', 'citation', 'done', 'error'
    data: Any

@router.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    """
    Ask a question and get a response with citations
    """
    try:
        rag_agent = RAGAgent()

        # Combine context if provided
        full_context = request.context or ""
        if request.selected_text:
            full_context += f"\n\nSelected text for context: {request.selected_text}"

        # Get response from RAG agent
        result = await rag_agent.query(request.query, context=full_context)

        return ChatResponse(
            response=result.get('response', ''),
            citations=result.get('citations', []),
            sources=result.get('sources', [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/ask-stream")
async def ask_question_stream(request: ChatRequest):
    """
    Ask a question and stream the response
    """
    async def event_generator():
        try:
            rag_agent = RAGAgent()

            # Combine context if provided
            full_context = request.context or ""
            if request.selected_text:
                full_context += f"\n\nSelected text for context: {request.selected_text}"

            # Get streaming response from RAG agent
            async for chunk in rag_agent.query_stream(request.query, context=full_context):
                # Yield the chunk as Server-Sent Event
                yield f"data: {json.dumps(chunk)}\n\n"

        except Exception as e:
            error_chunk = {
                "type": "error",
                "data": {"message": f"Error processing query: {str(e)}"}
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"
        finally:
            # Send done event
            done_chunk = {"type": "done", "data": {}}
            yield f"data: {json.dumps(done_chunk)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        }
    )

@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Chat API"}