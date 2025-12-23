from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
from src.agents.rag_agent import rag_agent

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
        # Get response from RAG agent (returns: answer, citations, reasoning, metadata)
        answer, citations, reasoning, metadata = await rag_agent.query(request.query, top_k=5)

        # Format citations for response
        citation_list = [
            {
                "chunk_id": c.chunk_id,
                "chapter": c.chapter,
                "section": c.section,
                "page": c.page,
                "score": c.score
            }
            for c in citations
        ]

        return ChatResponse(
            response=answer,
            citations=citation_list,
            sources=[f"Chapter {c.chapter}: {c.section}" for c in citations]
        )
    except Exception as e:
        error_msg = str(e)
        # Provide more specific error messages for common issues
        if "quota" in error_msg.lower():
            raise HTTPException(status_code=500, detail="OpenAI API quota exceeded. Please check your OpenAI billing and plan details.")
        elif "authentication" in error_msg.lower() or "invalid_api_key" in error_msg.lower():
            raise HTTPException(status_code=500, detail="Invalid OpenAI API key. Please check your API key configuration.")
        else:
            raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.post("/ask-stream")
async def ask_question_stream(request: ChatRequest):
    """
    Ask a question and stream the response
    """
    async def event_generator():
        try:
            # Combine context if provided
            full_context = request.context or ""
            if request.selected_text:
                full_context += f"\n\nSelected text for context: {request.selected_text}"

            # Get streaming response from RAG agent
            async for chunk in rag_agent.query_stream(request.query, context=full_context, top_k=5):
                # Yield the chunk as Server-Sent Event
                yield f"data: {json.dumps(chunk)}\n\n"

        except Exception as e:
            error_msg = str(e)
            # Provide more specific error messages for common issues in streaming
            if "quota" in error_msg.lower():
                error_chunk = {
                    "type": "error",
                    "data": {"message": "OpenAI API quota exceeded. Please check your OpenAI billing and plan details."}
                }
            elif "authentication" in error_msg.lower() or "invalid_api_key" in error_msg.lower():
                error_chunk = {
                    "type": "error",
                    "data": {"message": "Invalid OpenAI API key. Please check your API key configuration."}
                }
            else:
                error_chunk = {
                    "type": "error",
                    "data": {"message": f"Error processing query: {str(e)}"}
                }
            yield f"data: {json.dumps(error_chunk)}\n\n"

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