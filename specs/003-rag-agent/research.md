# Research Findings: RAG-Enabled Agent Service

## Overview
This document resolves all unknowns identified in the Technical Context section of the implementation plan for the RAG-Enabled Agent Service (003-rag-agent).

## Unknown 1: Specific OpenAI Model for the Agent

### Decision: Use GPT-4 Turbo (gpt-4-turbo) or GPT-4o
**Rationale**: Based on the spec which mentions "GPT-4o or latest stable model" as default, and considering that GPT-4o provides excellent reasoning capabilities for RAG applications while maintaining cost efficiency.

**Alternatives considered**:
- GPT-3.5 Turbo: Less capable for complex reasoning tasks
- GPT-4: More expensive than GPT-4o with similar capabilities
- Custom fine-tuned models: Premature optimization (violates YAGNI principle)

## Unknown 2: Qdrant Collection Name and Schema Details

### Decision: Use collection from Spec-1 with predefined schema
**Rationale**: The Qdrant collection was established in Spec-1 (Document Ingestion & Embedding). The schema includes:
- `id`: Unique chunk identifier
- `vector`: Embedding vector (likely 1536 dimensions for text-embedding-3-small)
- `payload`: Contains metadata fields:
  - `content`: The text content of the chunk
  - `chapter`: Chapter name/number from book
  - `section`: Section name/number from book
  - `page`: Page number (optional)
  - `source_document`: Original document identifier

**Alternatives considered**:
- Creating new collection: Would violate constraint of not re-embedding
- Different schema: Would require changes to Spec-1 implementation

## Unknown 3: Exact Structure of Book Content Metadata in Qdrant

### Decision: Use metadata fields as defined in Spec-1
**Rationale**: The document ingestion pipeline from Spec-1 already includes chapter, section, and page information in the Qdrant payload. The exact structure is:
```
payload: {
  "content": "text content of the chunk",
  "chapter": "Chapter 3",
  "section": "3.2 Control Systems",
  "page": 45,
  "source_document": "Physical_AI_Humanoid_Robotics.pdf",
  "chunk_id": "doc123_chunk_001"
}
```

**Alternatives considered**:
- Different metadata structure: Would require changes to existing ingestion pipeline
- Additional metadata fields: Would require re-processing existing documents

## Unknown 4: Token Limits for Agent Responses

### Decision: Use default limits from spec (4000 prompt tokens, 1000 completion tokens)
**Rationale**: The spec explicitly defines these limits in FR-013: "System MUST enforce max token limits for prompts and completions, with configurable thresholds (default: 4000 prompt tokens, 1000 completion tokens)"

**Alternatives considered**:
- Different limits: Would require justification and might impact performance
- Dynamic limits: Premature optimization that violates YAGNI principle

## Unknown 5: Exact Format for Citations in Response

### Decision: Use structured citation format with chunk_id, chapter, section, and score
**Rationale**: Based on FR-005 requiring "source citations referencing specific book chunks" and the available metadata fields. The format will be:
```
{
  "chunk_id": "unique_chunk_identifier",
  "chapter": "Chapter name/number",
  "section": "Section name/number",
  "page": 45,
  "score": 0.85
}
```

**Alternatives considered**:
- Simplified citations: Would lose important reference information
- Extended citations: Would add complexity without clear benefit

## Unknown 6: Environment Variable Names for Configuration

### Decision: Use standard naming convention following spec requirements
**Rationale**: Based on FR-002 requiring "connection parameters configurable via environment variables", the variables will be:
- `OPENAI_API_KEY`: OpenAI API key
- `QDRANT_URL`: Qdrant server URL
- `QDRANT_API_KEY`: Qdrant API key (if authentication required)
- `QDRANT_COLLECTION_NAME`: Name of the collection with book embeddings
- `OPENAI_MODEL`: OpenAI model name (default: gpt-4o)
- `TEMPERATURE`: Temperature setting (default: 0.1, max: 0.2 per FR-012)
- `TOP_K_DEFAULT`: Default top-k value (default: 5 per FR-003)

**Alternatives considered**:
- Different naming conventions: Would create inconsistency
- Configuration file: Would add complexity without benefit

## Unknown 7: Performance Benchmarks for Retrieval and Response Latency

### Decision: Use benchmarks defined in spec and constitution
**Rationale**: The spec defines clear performance requirements:
- Retrieval latency: p95 < 3 seconds (from NFR section)
- Response latency: p95 < 10 seconds (from NFR section)
- These align with the constitution's performance requirements

**Alternatives considered**:
- Different benchmarks: Would conflict with spec requirements
- More aggressive targets: Would require additional optimization work

## Implementation Readiness
All unknowns have been resolved based on:
1. Requirements explicitly stated in the feature spec
2. Constraints and requirements from the constitution
3. Existing infrastructure established in previous specs (Spec-1)

The implementation can proceed with confidence that all architectural decisions are aligned with the overall system requirements.