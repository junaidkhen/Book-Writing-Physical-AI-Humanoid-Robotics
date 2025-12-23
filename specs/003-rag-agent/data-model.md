# Data Models: RAG-Enabled Agent Service

## Overview
This document defines the data models for the RAG-Enabled Agent Service (003-rag-agent) based on the feature specification and requirements.

## Entity Models

### QueryRequest
**Purpose**: Input model for the /ask endpoint
**Validation Rules**:
- query: string, required, max 1000 characters
- top_k: integer, optional, range 1-20, default 5
- temperature: number, optional, range 0.0-0.2, default 0.1

**Fields**:
```
{
  query: string,        // User's natural language question (max 1000 chars)
  top_k?: integer,      // Number of chunks to retrieve (1-20, default 5)
  temperature?: number  // Temperature for agent response (0.0-0.2, default 0.1)
}
```

### QueryResponse
**Purpose**: Output model for the /ask endpoint
**Validation Rules**:
- answer: string, required
- citations: array of Citation, required
- reasoning: array of strings, required
- metadata: ResponseMetadata, required

**Fields**:
```
{
  answer: string,              // The agent's answer to the query
  citations: Citation[],       // List of citations for the answer
  reasoning: string[],         // Step-by-step reasoning process
  metadata: ResponseMetadata   // Additional metadata about the response
}
```

### Citation
**Purpose**: Represents a citation to a specific book chunk
**Validation Rules**:
- chunk_id: string, required
- chapter: string, required
- section: string, required
- score: number, required, range 0.0-1.0

**Fields**:
```
{
  chunk_id: string,    // Unique identifier for the book chunk
  chapter: string,     // Chapter reference in the book
  section: string,     // Section reference in the book
  page?: number,       // Page number (optional)
  score: number        // Similarity score (0.0-1.0)
}
```

### ResponseMetadata
**Purpose**: Metadata about the agent response and processing
**Validation Rules**:
- token_usage: TokenUsage, required
- retrieval_time: number, required, in milliseconds
- agent_time: number, required, in milliseconds
- total_time: number, required, in milliseconds
- chunks_retrieved: integer, required

**Fields**:
```
{
  token_usage: TokenUsage,    // Token usage statistics
  retrieval_time: number,     // Time for retrieval phase (ms)
  agent_time: number,         // Time for agent processing (ms)
  total_time: number,         // Total processing time (ms)
  chunks_retrieved: number    // Number of chunks retrieved
}
```

### TokenUsage
**Purpose**: Tracks token usage for API calls
**Validation Rules**:
- input_tokens: integer, required, >= 0
- output_tokens: integer, required, >= 0
- total_tokens: integer, required, >= 0

**Fields**:
```
{
  input_tokens: number,    // Number of input tokens used
  output_tokens: number,   // Number of output tokens generated
  total_tokens: number     // Total tokens (input + output)
}
```

### RetrievalRequest
**Purpose**: Input model for the /retrieve endpoint
**Validation Rules**:
- query: string, required, max 1000 characters
- top_k: integer, optional, range 1-20, default 5

**Fields**:
```
{
  query: string,        // User's search query (max 1000 chars)
  top_k?: integer       // Number of chunks to retrieve (1-20, default 5)
}
```

### RetrievalResponse
**Purpose**: Output model for the /retrieve endpoint
**Validation Rules**:
- chunks: array of RetrievedChunk, required
- metadata: RetrievalMetadata, required

**Fields**:
```
{
  chunks: RetrievedChunk[],    // Ranked list of retrieved chunks
  metadata: RetrievalMetadata  // Metadata about the retrieval
}
```

### RetrievedChunk
**Purpose**: Represents a single retrieved book chunk
**Validation Rules**:
- chunk_id: string, required
- content: string, required
- metadata: ChunkMetadata, required
- score: number, required, range 0.0-1.0

**Fields**:
```
{
  chunk_id: string,        // Unique identifier for the chunk
  content: string,         // The text content of the chunk
  metadata: ChunkMetadata, // Metadata about the chunk
  score: number            // Similarity score (0.0-1.0)
}
```

### ChunkMetadata
**Purpose**: Metadata about a book chunk
**Validation Rules**:
- chapter: string, required
- section: string, required
- source_document: string, required

**Fields**:
```
{
  chapter: string,            // Chapter in the book
  section: string,            // Section in the book
  page?: number,              // Page number (optional)
  source_document: string     // Original document identifier
}
```

### RetrievalMetadata
**Purpose**: Metadata about the retrieval operation
**Validation Rules**:
- query: string, required
- chunks_returned: integer, required, >= 0
- retrieval_time: number, required, in milliseconds
- similarity_threshold: number, required, range 0.0-1.0

**Fields**:
```
{
  query: string,                  // The original query
  chunks_returned: number,        // Number of chunks returned
  retrieval_time: number,         // Time taken for retrieval (ms)
  similarity_threshold: number    // Minimum similarity threshold used
}
```

### HealthResponse
**Purpose**: Output model for the /health endpoint
**Validation Rules**:
- status: enum of "healthy", "degraded", "unhealthy", required
- qdrant_status: string, required
- openai_status: string, required
- timestamp: string, required, ISO 8601 format

**Fields**:
```
{
  status: "healthy" | "degraded" | "unhealthy",  // Overall service status
  qdrant_status: string,                         // Qdrant connectivity status
  openai_status: string,                         // OpenAI API connectivity status
  timestamp: string                              // ISO 8601 timestamp
}
```

### MetricsResponse
**Purpose**: Output model for the /metadata endpoint
**Validation Rules**:
- config: ServiceConfig, required
- stats: PerformanceStats, required

**Fields**:
```
{
  config: ServiceConfig,      // Current service configuration
  stats: PerformanceStats     // Performance and usage statistics
}
```

### ServiceConfig
**Purpose**: Current service configuration
**Validation Rules**:
- model: string, required
- temperature: number, required, range 0.0-0.2
- top_k_default: integer, required, range 1-20
- max_tokens: number, required, >= 0
- qdrant_collection: string, required

**Fields**:
```
{
  model: string,              // OpenAI model being used
  temperature: number,        // Current temperature setting
  top_k_default: number,      // Default top-k value
  max_tokens: number,         // Maximum token limit
  qdrant_collection: string   // Qdrant collection name
}
```

### PerformanceStats
**Purpose**: Performance and usage statistics
**Validation Rules**:
- total_queries: integer, required, >= 0
- avg_response_time: number, required, >= 0
- error_count: integer, required, >= 0
- uptime: string, required

**Fields**:
```
{
  total_queries: number,           // Total number of queries processed
  avg_response_time: number,       // Average response time in ms
  avg_token_usage: TokenUsage,     // Average token usage
  error_count: number,             // Total number of errors
  uptime: string                   // Service uptime string
}
```

## API Schema Definitions

### OpenAPI Schema for /ask endpoint
```
POST /ask
Request Body: QueryRequest
Response 200: QueryResponse
Response 400: Error response for invalid input
Response 500: Error response for processing errors
```

### OpenAPI Schema for /retrieve endpoint
```
POST /retrieve
Request Body: RetrievalRequest
Response 200: RetrievalResponse
Response 400: Error response for invalid input
Response 500: Error response for retrieval errors
```

### OpenAPI Schema for /health endpoint
```
GET /health
Response 200: HealthResponse
Response 500: Error response for health check failures
```

### OpenAPI Schema for /metadata endpoint
```
GET /metadata
Response 200: MetricsResponse
Response 500: Error response for metrics errors
```

## Validation Rules Summary

### Input Validation
- Query length: Maximum 1000 characters
- top_k range: 1-20
- Temperature range: 0.0-0.2 (with default 0.1)
- Required fields: All non-optional fields must be present

### Output Validation
- All responses follow JSON schema
- Citations must reference actual retrieved chunks
- Token usage must be non-negative
- Timing values must be non-negative

## Relationships
- QueryRequest → QueryResponse (one-to-one for /ask endpoint)
- QueryRequest → RetrievedChunk[] (one-to-many through retrieval process)
- RetrievedChunk → Citation (one-to-one mapping)
- Multiple QueryRequest instances → PerformanceStats (aggregation)