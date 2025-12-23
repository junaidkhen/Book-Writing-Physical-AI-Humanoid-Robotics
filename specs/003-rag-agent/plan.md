# Implementation Plan: RAG-Enabled Agent Service

## Technical Context

**Feature**: 003-rag-agent - RAG-Enabled Agent Service
**Objective**: Implement a stateless RAG-enabled backend agent using the OpenAI Agents SDK and FastAPI that retrieves knowledge from Qdrant and produces grounded, citation-based answers from embedded book content.

### Current State
- OpenAI API key available in environment
- Qdrant collection with embedded book content exists from Spec-1
- Python 3.11+ environment available
- FastAPI framework available
- Need to implement retrieval, agent construction, and API endpoints
- Dependencies from spec: OpenAI API, Qdrant instance, Python 3.9+ with required libraries
- Book content already embedded and stored in Qdrant with metadata (chapter, section, page)
- Assumptions: Qdrant store is populated, OpenAI API key available, book metadata includes citation info

### Unknowns (NEEDS CLARIFICATION)
- Specific OpenAI model to use for the agent (default GPT-4o or latest stable model per spec) - RESOLVED in research.md
- Qdrant collection name and exact schema details (field names, data types) - RESOLVED in research.md
- Exact structure of book content metadata in Qdrant (chapter, section, page fields) - RESOLVED in research.md
- Token limits for the agent responses (default: 4000 prompt tokens, 1000 completion tokens per spec) - RESOLVED in research.md
- Exact format for citations in the response (chunk ID, chapter, section, page references) - RESOLVED in research.md
- Environment variable names for configuration (Qdrant URL, collection name, API keys) - RESOLVED in research.md
- Performance benchmarks for retrieval latency (p95 < 3 seconds) and response latency (p95 < 10 seconds) - RESOLVED in research.md

All unknowns have been resolved in research.md.

## Constitution Check

Based on `.specify/memory/constitution.md`, checking implementation alignment:

- ✅ **Data Integrity First**: Agent will preserve citation links to original book content and maintain traceability
- ✅ **API-First Design**: Will implement FastAPI endpoints with Pydantic models for request/response validation
- ✅ **Test-Driven Development**: Will write tests for API endpoints, retrieval logic, and agent responses before implementation
- ✅ **Security & Input Validation**: Will validate query inputs (length ≤ 1000 chars), sanitize requests, use environment variables for secrets
- ✅ **Performance & Scalability**: Will target p95 response times < 10 seconds and implement proper error handling for timeouts
- ✅ **Observability & Structured Logging**: Will include JSON-formatted logs with request IDs, tokens, latency metrics
- ✅ **Simplicity & YAGNI**: Will implement only required functionality without premature optimizations

### Gate: Architecture Alignment
- [x] Confirmed: Uses FastAPI for web framework (per spec FR-007, FR-008, FR-009, FR-010)
- [x] Confirmed: Uses Qdrant for vector storage (per spec FR-002, FR-003)
- [x] Confirmed: Uses OpenAI Agents SDK (per spec FR-001)
- [x] Confirmed: Stateless design as specified (per spec FR-014)

### Gate: Requirements Coverage
- [x] Confirmed: All phases from spec will be implemented (configuration, retrieval, agent, API, observability)
- [x] Confirmed: API endpoints match requirements (ask, retrieve, health, metadata per FR-007-010)
- [x] Confirmed: Retrieval functionality matches requirements (top-k, similarity threshold per FR-003)

### Gate: Constitution Principles Compliance
- [x] API-First Design: FastAPI with Pydantic models per II
- [x] Security & Input Validation: Query validation per IV
- [x] Observability: Structured logging with metrics per VI
- [x] Performance targets: Response time requirements per V
- [x] TDD approach: Tests before implementation per III
- [x] Simplicity: No over-engineering per VII

## Phase 0: Research & Discovery

### Research Tasks
1. OpenAI Agents SDK integration patterns and best practices for RAG applications
2. Qdrant query_points API usage for semantic search with metadata filtering
3. FastAPI best practices for async endpoints with proper error handling
4. Token management strategies for OpenAI models with configurable limits
5. Citation formatting patterns for academic and technical content
6. Performance optimization for vector similarity search and agent responses

### Expected Outcomes
- Clear understanding of OpenAI Agents SDK implementation for RAG use cases
- Confirmed Qdrant collection schema and query patterns for book content
- Defined citation format for responses with chapter/section references
- Performance benchmarks and optimization strategies
- Error handling patterns for service resilience

## Phase 1: Data Model & Contracts

### Data Models
- QueryRequest: {query: string, top_k?: number, temperature?: number} (max 1000 chars, top_k 1-20, temperature ≤ 0.2)
- QueryResponse: {answer: string, citations: Citation[], reasoning: string[], metadata: ResponseMetadata}
- Citation: {chunk_id: string, chapter: string, section: string, page?: number, score: number}
- ResponseMetadata: {token_usage: TokenUsage, retrieval_time: number, agent_time: number, total_time: number, chunks_retrieved: number}
- TokenUsage: {input_tokens: number, output_tokens: number, total_tokens: number}
- RetrievalRequest: {query: string, top_k?: number} (max 1000 chars, top_k 1-20)
- RetrievalResponse: {chunks: RetrievedChunk[], metadata: RetrievalMetadata}
- RetrievedChunk: {chunk_id: string, content: string, metadata: ChunkMetadata, score: number}
- ChunkMetadata: {chapter: string, section: string, page?: number, source_document: string}
- RetrievalMetadata: {query: string, chunks_returned: number, retrieval_time: number, similarity_threshold: number}
- HealthResponse: {status: "healthy" | "degraded" | "unhealthy", qdrant_status: string, openai_status: string, timestamp: string}
- MetricsResponse: {config: ServiceConfig, stats: PerformanceStats}
- ServiceConfig: {model: string, temperature: number, top_k_default: number, max_tokens: number, qdrant_collection: string}
- PerformanceStats: {total_queries: number, avg_response_time: number, avg_token_usage: TokenUsage, error_count: number, uptime: string}

### API Contracts
- POST /ask: Process query and return grounded answer with citations (FR-007)
  - Request: QueryRequest
  - Response: QueryResponse
  - Error: 400 for invalid input, 500 for processing errors
- POST /retrieve: Raw retrieval results only (FR-008)
  - Request: RetrievalRequest
  - Response: RetrievalResponse
  - Error: 400 for invalid input, 500 for retrieval errors
- GET /health: Service and Qdrant connectivity status (FR-009)
  - Response: HealthResponse
  - Error: 500 if service cannot determine health
- GET /metadata: Configuration and performance metrics (FR-010)
  - Response: MetricsResponse
  - Error: 500 for metrics errors

## Phase 2: Implementation Strategy

### Service Configuration & Bootstrap (Phase 1)
- Load configuration from .env file with validation (FR-002)
- Initialize FastAPI app with CORS middleware for future frontend integration
- Initialize Qdrant client with connection parameters
- Configure OpenAI agent settings (model, temperature ≤ 0.2, token limits)
- Set up structured logging with JSON formatter
- Initialize metrics collection system

### Retrieval Layer (Phase 2)
- Implement semantic search using Qdrant query_points API (FR-003)
- Handle configurable top_k parameter (default: 5, range: 1-20) (FR-003)
- Enforce similarity threshold and empty-result handling
- Return ranked chunks with metadata (chunk_id, chapter, section, score) (FR-016)
- Add performance monitoring for retrieval latency
- Implement error handling for Qdrant connectivity issues

### Agent Construction (Phase 3)
- Create OpenAI agent with retrieved context as primary knowledge source (FR-004)
- Implement grounded answering enforcement with explicit instructions to avoid hallucination (FR-004)
- Structure agent reasoning steps: query interpretation → retrieval summary → answer synthesis (FR-006)
- Generate citations tied to chunk metadata (FR-005)
- Implement token limit enforcement with intelligent context truncation
- Add deterministic behavior with temperature ≤ 0.2 (FR-012, FR-013)

### API Endpoints (Phase 4)
- Implement /ask endpoint with full RAG pipeline (retrieve → reason → answer) (FR-007)
- Implement /retrieve endpoint for raw retrieval results (FR-008)
- Implement /health endpoint with service and Qdrant connectivity status (FR-009)
- Implement /metadata endpoint with configuration and performance metrics (FR-010)
- Add comprehensive input validation (length ≤ 1000 chars, required fields) (FR-016)
- Return standardized JSON responses with proper error handling (FR-017)
- Add rate limiting and timeout handling

### Observability & Safety (Phase 5)
- Add structured logging for each request with: request ID, query, retrieved chunk count, token usage, latency (FR-011)
- Log retrieval time, agent processing time, and total time separately
- Handle edge cases gracefully: empty Qdrant, no relevant chunks, token truncation, malformed input (FR-015)
- Implement deterministic behavior and enforce token limits (FR-012, FR-013)
- Add monitoring for performance metrics and error rates
- Implement graceful degradation when Qdrant is unavailable

## Phase 3: Validation & Testing (Phase 6)

### Manual Tests
- In-scope question → grounded answer + citations (SC-002)
- Out-of-scope question → refusal without hallucination (SC-002)
- Retrieval-only verification with proper chunk ranking (SC-003)
- Edge case handling (empty results, connection failures, malformed input) (SC-009)
- Performance validation (response times under 10 seconds) (SC-001)
- Token usage within limits (SC-010)
- Deterministic behavior with consistent responses for identical queries (SC-008)

### Success Criteria
- All SC-001 → SC-010 criteria achievable and validated
- No re-embedding or data mutation occurs (per constraints)
- Performance within acceptable bounds (latency, throughput targets)
- Full API compliance with all functional requirements
- Proper error handling and graceful degradation