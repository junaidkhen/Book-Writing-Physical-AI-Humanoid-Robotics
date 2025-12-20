# Data Model: Retrieval Pipeline Validation

**Feature**: 001-retrieval-pipeline-validation
**Date**: 2025-12-16
**Purpose**: Define entities, attributes, relationships, and validation rules

## Entity Definitions

### 1. TestQuery

**Purpose**: Represents a single test query used for retrieval validation

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `id` | integer | Yes | Unique identifier for the query | > 0, unique within test dataset |
| `query` | string | Yes | Natural language query text | Non-empty after whitespace trim |
| `category` | string | Yes | Query classification | One of: concept, process, technical, analysis, future, edge_case |
| `expected_relevance` | string | Yes | Expected result quality | One of: high, medium, low |
| `description` | string | Yes | Human-readable explanation of query purpose | Non-empty |

**Example**:
```json
{
  "id": 1,
  "query": "What is physical AI?",
  "category": "concept",
  "expected_relevance": "high",
  "description": "Core concept query about physical AI"
}
```

**Relationships**:
- One TestQuery → Many QueryResults (1:N relationship)
- Stored in: `validation/spec2/test_queries.json`

**State Transitions**: Immutable (test queries are static, do not change during execution)

---

### 2. QueryResult

**Purpose**: Represents the execution outcome of a single test query, including retrieved chunks and performance metrics

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `query_id` | integer | Yes | Reference to TestQuery.id | Must match existing TestQuery |
| `query_text` | string | Yes | Copy of query text for readability | Matches TestQuery.query |
| `category` | string | Yes | Copy of category for reporting | Matches TestQuery.category |
| `status` | string | Yes | Execution status | One of: success, error, skipped |
| `latency_ms` | float | If status=success | Query execution time in milliseconds | ≥ 0 |
| `retrieved_chunks` | array[RetrievedChunk] | If status=success | Top-k results from Qdrant | Length ≤ top_k parameter |
| `error_message` | string | If status=error | Detailed error description | Non-empty if status=error |
| `timestamp` | string (ISO 8601) | Yes | When query was executed | Valid datetime format |

**Example**:
```json
{
  "query_id": 1,
  "query_text": "What is physical AI?",
  "category": "concept",
  "status": "success",
  "latency_ms": 342.5,
  "retrieved_chunks": [...],
  "timestamp": "2025-12-16T14:35:22Z"
}
```

**Relationships**:
- One QueryResult → Many RetrievedChunks (1:N relationship)
- Stored in: `validation/spec2/results.json`

**State Transitions**:
1. **Pending** (before execution)
2. **Success** (retrieved chunks successfully)
3. **Error** (API failure, connection issue, etc.)
4. **Skipped** (invalid input, e.g., empty query)

**Invariants**:
- If status=success, retrieved_chunks must be non-empty (unless corpus has no matches)
- If status=error, error_message must be present
- latency_ms only present if status=success

---

### 3. RetrievedChunk

**Purpose**: Represents a single document chunk retrieved from Qdrant in response to a query

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `vector_id` | string | Yes | Qdrant point ID (UUID) | Valid UUID format |
| `score` | float | Yes | Cosine similarity score | -1.0 ≤ score ≤ 1.0 |
| `source_url` | string | Yes (per FR-003) | Original document URL | Valid URL format, non-empty |
| `text` | string | Yes (per FR-003) | Original text excerpt from chunk | Non-empty (per FR-005) |
| `chunk_index` | integer | Yes | Position of chunk within source document | ≥ 0 |
| `document_metadata` | object | Optional | Additional metadata from ingestion | May include: title, author, publish_date, etc. |
| `relevance_label` | string | Computed | Rule-based relevance classification | One of: High, Medium, Low, Incorrect |

**Example**:
```json
{
  "vector_id": "a3f2d9c8-1234-5678-90ab-cdef12345678",
  "score": 0.87,
  "source_url": "https://example.com/physical-ai-chapter1",
  "text": "Physical AI refers to artificial intelligence systems that interact with the physical world through robotic embodiments...",
  "chunk_index": 3,
  "document_metadata": {
    "title": "Introduction to Physical AI",
    "section": "Chapter 1: Foundations"
  },
  "relevance_label": "High"
}
```

**Relationships**:
- Many RetrievedChunks → One QueryResult (N:1 relationship)
- Many RetrievedChunks → One Qdrant Point (N:1, same chunk can be retrieved by multiple queries)

**Validation Rules**:
- **FR-003**: MUST include score, vector_id, source_url, text
- **FR-005**: MUST validate metadata completeness (source_url and text non-empty)
- **FR-011**: Score MUST be in valid range for cosine similarity

**Relevance Labeling** (computed field, not stored in Qdrant):
- **High**: score ≥ 0.78
- **Medium**: 0.60 ≤ score < 0.78
- **Low**: 0.40 ≤ score < 0.60
- **Incorrect**: score < 0.40

---

### 4. ValidationReport

**Purpose**: Aggregated metrics and summary of entire validation run

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `report_timestamp` | string (ISO 8601) | Yes | When validation was executed | Valid datetime |
| `total_queries` | integer | Yes | Number of queries attempted | ≥ 0 |
| `successful_queries` | integer | Yes | Queries with status=success | ≤ total_queries |
| `failed_queries` | integer | Yes | Queries with status=error | ≤ total_queries |
| `skipped_queries` | integer | Yes | Queries with status=skipped | ≤ total_queries |
| `performance_metrics` | PerformanceMetrics | Yes | Latency statistics | See PerformanceMetrics |
| `quality_metrics` | QualityMetrics | Yes | Relevance and ranking statistics | See QualityMetrics |
| `integrity_metrics` | IntegrityMetrics | Yes | Data completeness checks | See IntegrityMetrics |
| `success_criteria_status` | object | Yes | SC-001 through SC-008 pass/fail | Boolean for each criterion |

**Example**:
```json
{
  "report_timestamp": "2025-12-16T14:45:00Z",
  "total_queries": 20,
  "successful_queries": 18,
  "failed_queries": 0,
  "skipped_queries": 2,
  "performance_metrics": {...},
  "quality_metrics": {...},
  "integrity_metrics": {...},
  "success_criteria_status": {
    "SC-001": true,
    "SC-002": true,
    ...
  }
}
```

**Relationships**:
- One ValidationReport → Many QueryResults (1:N, aggregates all queries)
- Stored in: `validation/spec2/report.md` (Markdown format, derived from this data model)

**Invariants**:
- total_queries = successful_queries + failed_queries + skipped_queries
- success_criteria_status must have exactly 8 keys (SC-001 through SC-008)

---

### 5. PerformanceMetrics

**Purpose**: Latency statistics for validation run (embedded in ValidationReport)

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `average_latency_ms` | float | Yes | Mean latency across all successful queries | ≥ 0 |
| `p50_latency_ms` | float | Yes | Median latency (50th percentile) | ≥ 0 |
| `p95_latency_ms` | float | Yes | 95th percentile latency | ≥ p50 |
| `min_latency_ms` | float | Yes | Fastest query | ≥ 0 |
| `max_latency_ms` | float | Yes | Slowest query | ≥ average |

**Example**:
```json
{
  "average_latency_ms": 342.8,
  "p50_latency_ms": 310.2,
  "p95_latency_ms": 478.5,
  "min_latency_ms": 245.1,
  "max_latency_ms": 512.3
}
```

**Success Criteria Mapping**:
- **SC-004**: average_latency_ms < 500 (target met if true)

---

### 6. QualityMetrics

**Purpose**: Relevance and ranking quality statistics (embedded in ValidationReport)

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `average_similarity_score` | float | Yes | Mean score across all retrieved chunks | 0.0 ≤ score ≤ 1.0 |
| `score_distribution` | object | Yes | Count of High/Medium/Low/Incorrect labels | See below |
| `monotonic_decrease_pass_rate` | float | Yes | % of queries with monotonic score decrease | 0.0 ≤ rate ≤ 1.0 |
| `top3_relevance_rate` | float | Optional | % of queries with relevant top-3 (manual validation) | 0.0 ≤ rate ≤ 1.0 |

**score_distribution**:
```json
{
  "High": 120,     // Count of chunks with score ≥ 0.78
  "Medium": 45,    // Count of chunks with 0.60 ≤ score < 0.78
  "Low": 15,       // Count of chunks with 0.40 ≤ score < 0.60
  "Incorrect": 0   // Count of chunks with score < 0.40
}
```

**Example**:
```json
{
  "average_similarity_score": 0.75,
  "score_distribution": {
    "High": 120,
    "Medium": 45,
    "Low": 15,
    "Incorrect": 0
  },
  "monotonic_decrease_pass_rate": 0.95,
  "top3_relevance_rate": 0.85
}
```

**Success Criteria Mapping**:
- **SC-003**: monotonic_decrease_pass_rate ≥ 0.90 (90% of queries)
- **SC-006**: top3_relevance_rate ≥ 0.80 (80% of queries) — **Manual validation required**

---

### 7. IntegrityMetrics

**Purpose**: Data completeness and corpus health checks (embedded in ValidationReport)

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `total_vectors_in_collection` | integer | Yes | Point count from Qdrant | ≥ 0 |
| `sample_size` | integer | Yes | Number of vectors checked (5% sample) | ≥ 0 |
| `valid_payload_count` | integer | Yes | Vectors with complete metadata | ≤ sample_size |
| `valid_payload_percentage` | float | Yes | (valid / sample_size) × 100 | 0.0 ≤ pct ≤ 100.0 |
| `missing_url_count` | integer | Yes | Vectors with missing/empty source_url | ≥ 0 |
| `missing_text_count` | integer | Yes | Vectors with missing/empty text | ≥ 0 |

**Example**:
```json
{
  "total_vectors_in_collection": 537,
  "sample_size": 27,
  "valid_payload_count": 27,
  "valid_payload_percentage": 100.0,
  "missing_url_count": 0,
  "missing_text_count": 0
}
```

**Success Criteria Mapping**:
- **SC-002**: valid_payload_percentage = 100.0 (all chunks have complete metadata)
- **SC-005**: missing_url_count = 0 AND missing_text_count = 0 (zero integrity issues)
- **SC-008**: Verified by checking total_vectors_in_collection > 0 and schema validation passes

---

### 8. EmbeddingModelReference

**Purpose**: Configuration details for the Cohere embedding model used (from Spec-1, reused here)

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `model_name` | string | Yes | Cohere model identifier | "embed-english-v3.0" (must match Spec-1) |
| `model_version` | string | Optional | Model version string | e.g., "v3.0" |
| `embedding_dimensions` | integer | Yes | Vector dimensionality | 1024 (for embed-english-v3.0) |
| `max_tokens` | integer | Yes | Maximum input token limit | 512 (Cohere limit) |
| `distance_metric` | string | Yes | Qdrant similarity metric | "cosine" (must match Qdrant collection) |

**Example**:
```json
{
  "model_name": "embed-english-v3.0",
  "model_version": "v3.0",
  "embedding_dimensions": 1024,
  "max_tokens": 512,
  "distance_metric": "cosine"
}
```

**Relationships**:
- Referenced by Qdrant Collection schema (distance_metric, vector_size must match)
- Referenced in validation report (confirms consistency with Spec-1)

**Invariants**:
- **FR-002**: model_name MUST match the model used in Spec-1 ingestion
- **FR-008**: distance_metric MUST match Qdrant collection configuration

---

### 9. QdrantCollection

**Purpose**: Metadata about the Qdrant vector collection (from Spec-1, validated in Spec-2)

**Attributes**:
| Field | Type | Required | Description | Validation Rules |
|-------|------|----------|-------------|------------------|
| `collection_name` | string | Yes | Name of Qdrant collection | "documents" (hardcoded in Spec-1) |
| `vector_size` | integer | Yes | Embedding dimensionality | 1024 (must match EmbeddingModelReference) |
| `distance_metric` | string | Yes | Similarity calculation method | "Cosine" (Qdrant enum value) |
| `point_count` | integer | Yes | Total vectors stored | ≥ 0 |
| `indexed` | boolean | Yes | Whether collection is indexed | true (required for queries) |

**Example**:
```json
{
  "collection_name": "documents",
  "vector_size": 1024,
  "distance_metric": "Cosine",
  "point_count": 537,
  "indexed": true
}
```

**Relationships**:
- Contains Many RetrievedChunks (1:N, collection stores all chunks)
- Referenced by ValidationReport.integrity_metrics.total_vectors_in_collection

**Invariants**:
- **SC-008**: Collection schema MUST match expected configuration (vector_size=1024, distance_metric=Cosine)
- **FR-008**: Validation MUST verify schema before running queries

---

## Entity Relationship Diagram

```
┌─────────────────┐
│   TestQuery     │ 1
│  (test_queries  │───┐
│    .json)       │   │
└─────────────────┘   │
                       │ 1:N
                       │
                       ▼ N
                 ┌─────────────────┐
                 │  QueryResult    │
                 │  (results.json) │
                 └─────────────────┘
                       │
                       │ 1:N
                       │
                       ▼ N
                 ┌──────────────────┐
                 │ RetrievedChunk   │
                 │ (embedded in     │
                 │  QueryResult)    │
                 └──────────────────┘
                       │
                       │ N:1
                       │
                       ▼ 1
                 ┌──────────────────┐
                 │ QdrantCollection │
                 │  (Qdrant Cloud)  │
                 └──────────────────┘

┌─────────────────────┐
│ ValidationReport    │ 1
│  (report.md)        │───┐
│                     │   │ Aggregates
└─────────────────────┘   │
                           ▼ N
                    ┌──────────────┐
                    │ QueryResult  │
                    └──────────────┘
```

## Data Flow

1. **Input**: Load TestQuery[] from `validation/spec2/test_queries.json`
2. **Execution**:
   - For each TestQuery:
     a. Validate query input (empty check, token limit check)
     b. Embed query using Cohere API (EmbeddingModelReference)
     c. Query Qdrant collection (QdrantCollection)
     d. Retrieve top-k RetrievedChunk[]
     e. Measure latency
     f. Create QueryResult
3. **Aggregation**:
   - Compute PerformanceMetrics from QueryResult[]
   - Compute QualityMetrics from RetrievedChunk[] relevance labels
   - Compute IntegrityMetrics by sampling QdrantCollection
   - Evaluate success_criteria_status
   - Generate ValidationReport
4. **Output**:
   - Write QueryResult[] to `validation/spec2/results.json`
   - Write ValidationReport to `validation/spec2/report.md` (Markdown format)

## Validation Rules Summary

| Entity | Key Validation | Spec Reference |
|--------|----------------|----------------|
| TestQuery | Non-empty query text after trim | FR-014 (empty query handling) |
| QueryResult | status=success → retrieved_chunks non-empty | FR-001, SC-001 |
| RetrievedChunk | source_url and text MUST be non-empty | FR-003, FR-005, SC-002 |
| RetrievedChunk | score in range [-1.0, 1.0] | FR-011 |
| PerformanceMetrics | average_latency_ms < 500 | SC-004 |
| QualityMetrics | monotonic_decrease_pass_rate ≥ 0.90 | SC-003 |
| IntegrityMetrics | valid_payload_percentage = 100.0 | SC-002, SC-005 |
| QdrantCollection | vector_size=1024, distance_metric=Cosine | FR-008, SC-008 |

## Implementation Notes

- All entities except QdrantCollection are Python dictionaries/dataclasses (no formal ORM)
- QdrantCollection is accessed via `qdrant_client.get_collection()` API
- ValidationReport is generated as Markdown (human-readable) but internally structured as this data model
- Relevance labels (High/Medium/Low/Incorrect) are computed at runtime, not stored in Qdrant
- Manual validation for SC-006 (top3_relevance_rate) requires updating `top3_relevance_rate` field after human review

## Future Enhancements

1. **Ground Truth Labels**: Add `expected_chunk_ids` to TestQuery for automated precision/recall calculation
2. **Temporal Tracking**: Add `validation_run_id` to track multiple validation runs over time
3. **Diff Reports**: Compare ValidationReports across runs to detect retrieval quality regressions
4. **Export Formats**: Generate JSON schema for ValidationReport to enable programmatic parsing
