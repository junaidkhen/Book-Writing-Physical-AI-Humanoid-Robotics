# Data Model: Document Ingestion Core System

**Feature**: 002-document-ingestion-core
**Date**: 2025-12-17
**Purpose**: Define core entities, relationships, and storage schemas for document ingestion pipeline

## Entity Overview

The document ingestion system manages three core entities:

1. **Document**: Original file metadata and processing status
2. **Chunk**: Text segments extracted from documents with positional metadata
3. **IngestionJob**: Batch processing tracker for multiple documents

**Storage Strategy**:
- **Qdrant**: Primary storage for Chunks with denormalized Document metadata
- **Optional**: Local filesystem for original document archival (future enhancement)

---

## Entity 1: Document

### Purpose
Represents a single ingested file (PDF, TXT, DOCX, HTML, or URL content) with metadata for tracking, deduplication, and retrieval filtering.

### Fields

| Field Name | Type | Required | Description | Validation Rules |
|------------|------|----------|-------------|------------------|
| `document_id` | UUID (string) | Yes | Unique identifier for document | UUID v4 format |
| `filename` | string | Yes | Original filename or URL path | Max 255 chars, sanitized |
| `content_type` | enum | Yes | Document format | One of: `pdf`, `txt`, `docx`, `html` |
| `content_hash` | string | Yes | SHA-256 hash of normalized text | 64-char hexadecimal |
| `file_size_bytes` | integer | Yes | Original file size in bytes | 0 < size ≤ 524288000 (500MB) |
| `source_url` | string | No | URL if ingested from web | Valid http/https URL or null |
| `upload_date` | datetime (ISO 8601) | Yes | Timestamp of ingestion initiation | UTC timezone |
| `processing_status` | enum | Yes | Current processing state | One of: `pending`, `processing`, `completed`, `failed` |
| `processing_started_at` | datetime | No | When processing began | UTC, null if not started |
| `processing_completed_at` | datetime | No | When processing finished | UTC, null if not completed |
| `chunk_count` | integer | No | Number of chunks generated | ≥ 0, null if not processed |
| `error_message` | string | No | Error detail if processing failed | Max 1000 chars, null if successful |
| `ingestion_job_id` | UUID (string) | No | Parent job if part of batch | UUID v4 or null for single ingestion |

### Example (JSON)

```json
{
  "document_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "filename": "robotics-chapter-1.pdf",
  "content_type": "pdf",
  "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "file_size_bytes": 2457600,
  "source_url": null,
  "upload_date": "2025-12-17T10:30:00Z",
  "processing_status": "completed",
  "processing_started_at": "2025-12-17T10:30:01Z",
  "processing_completed_at": "2025-12-17T10:30:15Z",
  "chunk_count": 42,
  "error_message": null,
  "ingestion_job_id": null
}
```

### Relationships

- **One-to-Many with Chunk**: One Document → Many Chunks (via `document_id` foreign key)
- **Many-to-One with IngestionJob**: Many Documents → One IngestionJob (via `ingestion_job_id`)

### Storage Implementation

**Qdrant Payload** (denormalized in each Chunk point):
```python
# Document metadata stored redundantly in each chunk for single-query retrieval
chunk_payload = {
    "document_metadata": {
        "document_id": "a1b2c3d4-...",
        "filename": "robotics-chapter-1.pdf",
        "content_type": "pdf",
        "content_hash": "e3b0c44...",
        "upload_date": "2025-12-17T10:30:00Z",
        "source_url": None
    },
    # ... chunk-specific fields
}
```

### Indexes

- **Primary Key**: `document_id` (UUID)
- **Unique Index**: `content_hash` (for duplicate detection)
- **Index**: `processing_status` (for querying pending/failed jobs)
- **Index**: `ingestion_job_id` (for batch queries)

---

## Entity 2: Chunk

### Purpose
Represents a semantically meaningful text segment extracted from a Document, with positional metadata for reconstruction and embedding storage for RAG retrieval.

### Fields

| Field Name | Type | Required | Description | Validation Rules |
|------------|------|----------|-------------|------------------|
| `chunk_id` | UUID (string) | Yes | Unique identifier for chunk | UUID v4 format, also Qdrant point ID |
| `document_id` | UUID (string) | Yes | Parent document reference | Must exist in Documents |
| `chunk_index` | integer | Yes | Sequential position in document | ≥ 0, unique within document |
| `text_content` | string | Yes | Extracted text segment | 500 ≤ length ≤ 2000 chars |
| `char_count` | integer | Yes | Number of characters in chunk | Equals `len(text_content)` |
| `start_position` | integer | No | Character offset in original document | ≥ 0, null if unknown |
| `end_position` | integer | No | End character offset in original | > start_position, null if unknown |
| `embedding_vector` | float[] | No | Cohere embedding (1024 dimensions) | Dimension=1024, null before embedding |
| `embedding_model` | string | No | Model used for embedding | e.g., "embed-english-v3.0" |
| `created_at` | datetime | Yes | Chunk creation timestamp | UTC timezone |

**Note**: Additional document metadata fields are denormalized in Qdrant payload (see Document entity).

### Example (JSON)

```json
{
  "chunk_id": "f1e2d3c4-5678-90ab-cdef-0987654321ab",
  "document_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "chunk_index": 0,
  "text_content": "Chapter 1: Introduction to Physical AI and Humanoid Robotics. Physical AI represents the convergence of artificial intelligence, robotics, and embodied cognition...",
  "char_count": 987,
  "start_position": 0,
  "end_position": 987,
  "embedding_vector": [0.123, -0.456, 0.789, ...],  // 1024 floats
  "embedding_model": "embed-english-v3.0",
  "created_at": "2025-12-17T10:30:05Z"
}
```

### Relationships

- **Many-to-One with Document**: Many Chunks → One Document (via `document_id`)

### Storage Implementation

**Qdrant Collection Schema**:
```python
from qdrant_client import QdrantClient
from qdrant_client.http import models

client.create_collection(
    collection_name="documents",
    vectors_config=models.VectorParams(
        size=1024,  # Cohere embed-english-v3.0 dimension
        distance=models.Distance.COSINE
    )
)

# Upsert chunk as Qdrant point
client.upsert(
    collection_name="documents",
    points=[
        models.PointStruct(
            id=chunk_id,  # UUID string
            vector=embedding_vector,  # 1024-dim float array
            payload={
                "document_id": "a1b2c3d4-...",
                "chunk_index": 0,
                "text_content": "Chapter 1: Introduction...",
                "char_count": 987,
                "start_position": 0,
                "end_position": 987,
                "embedding_model": "embed-english-v3.0",
                "created_at": "2025-12-17T10:30:05Z",
                # Denormalized document metadata for single-query retrieval
                "document_metadata": {
                    "filename": "robotics-chapter-1.pdf",
                    "content_type": "pdf",
                    "content_hash": "e3b0c44...",
                    "upload_date": "2025-12-17T10:30:00Z",
                    "source_url": None
                }
            }
        )
    ]
)
```

### Indexes (Qdrant Payload Indexing)

- **Field Index**: `document_id` (for filtering by parent document)
- **Field Index**: `chunk_index` (for ordering chunks)
- **Field Index**: `document_metadata.content_hash` (for duplicate checks)

---

## Entity 3: IngestionJob

### Purpose
Tracks batch ingestion operations processing multiple documents, enabling progress monitoring, error aggregation, and retry logic.

### Fields

| Field Name | Type | Required | Description | Validation Rules |
|------------|------|----------|-------------|------------------|
| `job_id` | UUID (string) | Yes | Unique identifier for job | UUID v4 format |
| `job_type` | enum | Yes | Single or batch ingestion | One of: `single`, `batch` |
| `total_documents` | integer | Yes | Number of documents in job | 1 ≤ count ≤ 100 (per FR-010) |
| `documents_processed` | integer | Yes | Count of completed documents | 0 ≤ count ≤ total_documents |
| `documents_failed` | integer | Yes | Count of failed documents | 0 ≤ count ≤ total_documents |
| `status` | enum | Yes | Overall job status | One of: `pending`, `processing`, `completed`, `failed`, `partial_success` |
| `started_at` | datetime | Yes | Job start timestamp | UTC timezone |
| `completed_at` | datetime | No | Job completion timestamp | UTC, null if not completed |
| `error_logs` | array[object] | Yes | Per-document error details | Array of `{document_id, error_message}` |
| `document_ids` | array[UUID] | Yes | List of documents in this job | Array of valid UUIDs |

### Example (JSON)

```json
{
  "job_id": "b2c3d4e5-6789-01ab-cdef-2345678901bc",
  "job_type": "batch",
  "total_documents": 10,
  "documents_processed": 8,
  "documents_failed": 2,
  "status": "partial_success",
  "started_at": "2025-12-17T11:00:00Z",
  "completed_at": "2025-12-17T11:05:30Z",
  "error_logs": [
    {
      "document_id": "x1y2z3...",
      "error_message": "Unsupported file type: .exe"
    },
    {
      "document_id": "a2b3c4...",
      "error_message": "File exceeds 500MB limit: 612.3MB"
    }
  ],
  "document_ids": [
    "d1e2f3...",
    "g4h5i6...",
    "x1y2z3...",  // Failed
    "a2b3c4...",  // Failed
    // ... 6 more
  ]
}
```

### Relationships

- **One-to-Many with Document**: One IngestionJob → Many Documents (via `ingestion_job_id` in Document)

### Storage Implementation

**Option 1: Qdrant Payload** (lightweight, no separate DB):
```python
# Store job metadata in a special Qdrant collection
client.upsert(
    collection_name="ingestion_jobs",
    points=[
        models.PointStruct(
            id=job_id,
            vector=[0.0] * 128,  # Dummy vector (jobs not searchable by similarity)
            payload={
                "job_type": "batch",
                "total_documents": 10,
                "documents_processed": 8,
                "documents_failed": 2,
                "status": "partial_success",
                "started_at": "2025-12-17T11:00:00Z",
                "completed_at": "2025-12-17T11:05:30Z",
                "error_logs": [...],
                "document_ids": [...]
            }
        )
    ]
)
```

**Option 2: In-memory** (simplest for MVP, ephemeral):
- Store jobs in Python dict during processing
- Lose history on server restart (acceptable for MVP per YAGNI)
- Persist logs to filesystem for debugging

**Decision**: Start with Option 2 (in-memory), migrate to Option 1 if persistence needed.

### Status Transitions

```
pending → processing → completed
                    → failed
                    → partial_success (some docs failed)
```

---

## Entity Relationships Diagram

```
┌─────────────────┐
│  IngestionJob   │
│  job_id (PK)    │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│     Document        │
│  document_id (PK)   │
│  ingestion_job_id   │◄─── content_hash (UNIQUE INDEX for duplicates)
│  content_hash       │
└────────┬────────────┘
         │ 1
         │
         │ N
┌────────▼────────────┐
│      Chunk          │
│  chunk_id (PK)      │
│  document_id (FK)   │
│  embedding_vector   │
└─────────────────────┘
```

---

## Validation Rules Summary

### Document
- `file_size_bytes`: 0 < size ≤ 500MB (524,288,000 bytes)
- `content_hash`: Must be unique (duplicate check)
- `chunk_count`: ≥ 0 if processed, null if pending
- `processing_status`: Must transition `pending` → `processing` → `completed`/`failed`

### Chunk
- `text_content`: 500 ≤ length ≤ 2000 characters (per FR-003)
- `chunk_index`: Unique within `document_id`, sequential (0, 1, 2, ...)
- `embedding_vector`: Exactly 1024 dimensions if present
- `char_count`: Must equal `len(text_content)`

### IngestionJob
- `total_documents`: 1 ≤ count ≤ 100 (per FR-010 batch limit)
- `documents_processed + documents_failed ≤ total_documents`
- `status = partial_success` iff `documents_failed > 0 AND documents_processed > 0`
- `status = failed` iff `documents_processed = 0 AND documents_failed > 0`

---

## Migration Notes

### From Existing main.py

Current `main.py` stores vectors directly in Qdrant without explicit Document/Chunk entities. Migration path:

1. **Preserve existing Qdrant collection** ("documents")
2. **Add metadata fields** to existing points (backfill with defaults)
3. **Introduce Document tracking** with new ingestion requests
4. **Gradual schema migration**: Update payloads during next re-indexing

### Future Enhancements

- **Document versioning**: Add `version` field to track updates
- **User ownership**: Add `user_id` for multi-tenant support
- **Tags/categories**: Add `tags` array for manual categorization
- **Original file storage**: Save original files to S3/local filesystem

---

## Summary

Three core entities defined with clear relationships, storage schemas, and validation rules:

1. **Document**: File metadata, processing status, deduplication via content_hash
2. **Chunk**: Text segments with embeddings, stored as Qdrant points
3. **IngestionJob**: Batch tracking with error aggregation

All entities align with:
- **Functional Requirements**: FR-004 (storage), FR-006 (duplicates), FR-010 (batch)
- **Constitution Principle I**: Data integrity via content hashing and atomic operations
- **Constitution Principle VII**: Simplicity via denormalization (no complex joins)

**Next**: Define API contracts in `contracts/` directory.
