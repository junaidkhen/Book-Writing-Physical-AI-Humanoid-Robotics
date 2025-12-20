from pydantic import BaseModel, Field
from typing import List, Optional


class TokenUsage(BaseModel):
    """
    Tracks token usage for API calls
    """
    input_tokens: int = Field(..., description="Number of input tokens used", ge=0)
    output_tokens: int = Field(..., description="Number of output tokens generated", ge=0)
    total_tokens: int = Field(..., description="Total tokens (input + output)", ge=0)


class Citation(BaseModel):
    """
    Represents a citation to a specific book chunk
    """
    chunk_id: str = Field(..., description="Unique identifier for the book chunk")
    chapter: str = Field(..., description="Chapter reference in the book")
    section: str = Field(..., description="Section reference in the book")
    page: Optional[int] = Field(None, description="Page number (optional)")
    score: float = Field(..., description="Similarity score (0.0-1.0)", ge=0.0, le=1.0)


class ResponseMetadata(BaseModel):
    """
    Metadata about the agent response and processing
    """
    token_usage: TokenUsage = Field(..., description="Token usage statistics")
    retrieval_time: float = Field(..., description="Time for retrieval phase (ms)", ge=0)
    agent_time: float = Field(..., description="Time for agent processing (ms)", ge=0)
    total_time: float = Field(..., description="Total processing time (ms)", ge=0)
    chunks_retrieved: int = Field(..., description="Number of chunks retrieved", ge=0)


class QueryResponse(BaseModel):
    """
    Output model for the /ask endpoint
    """
    answer: str = Field(..., description="The agent's answer to the query")
    citations: List[Citation] = Field(..., description="List of citations for the answer")
    reasoning: List[str] = Field(..., description="Step-by-step reasoning process")
    metadata: ResponseMetadata = Field(..., description="Additional metadata about the response")


class ChunkMetadata(BaseModel):
    """
    Metadata about a book chunk
    """
    chapter: str = Field(..., description="Chapter in the book")
    section: str = Field(..., description="Section in the book")
    page: Optional[int] = Field(None, description="Page number (optional)")
    source_document: str = Field(..., description="Original document identifier")


class RetrievedChunk(BaseModel):
    """
    Represents a single retrieved book chunk
    """
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="The text content of the chunk")
    metadata: ChunkMetadata = Field(..., description="Metadata about the chunk")
    score: float = Field(..., description="Similarity score (0.0-1.0)", ge=0.0, le=1.0)


class RetrievalMetadata(BaseModel):
    """
    Metadata about the retrieval operation
    """
    query: str = Field(..., description="The original query")
    chunks_returned: int = Field(..., description="Number of chunks returned", ge=0)
    retrieval_time: float = Field(..., description="Time taken for retrieval (ms)", ge=0)
    similarity_threshold: float = Field(default=0.0, description="Minimum similarity threshold used", ge=0.0, le=1.0)


class RetrievalResponse(BaseModel):
    """
    Output model for the /retrieve endpoint
    """
    chunks: List[RetrievedChunk] = Field(..., description="Ranked list of retrieved chunks")
    metadata: RetrievalMetadata = Field(..., description="Metadata about the retrieval")