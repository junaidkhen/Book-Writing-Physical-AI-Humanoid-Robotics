# API Contracts: Document Ingestion Core System

**Feature**: 002-document-ingestion-core
**Date**: 2025-12-17
**Purpose**: Define REST API contracts for document ingestion service

## Overview

This directory contains OpenAPI 3.0 specifications for the Document Ingestion API. These contracts serve as:

1. **Design blueprints** for implementation
2. **Test specifications** for contract testing
3. **Documentation** for API consumers
4. **Validation schemas** for request/response validation

## Files

- **`ingestion-api.yaml`**: Complete OpenAPI 3.0 specification for all endpoints

## API Summary

### Base URL

- **Local Development**: `http://localhost:8000/api/v1`
- **Production**: `https://api.example.com/api/v1`

### Endpoints

| Endpoint | Method | Purpose | Request Body | Response |
|----------|--------|---------|--------------|----------|
| `/ingest/file` | POST | Upload single file | `multipart/form-data` (file) | 202 Accepted + job_id |
| `/ingest/url` | POST | Ingest from URL | `application/json` (url) | 202 Accepted + job_id |
| `/ingest/batch` | POST | Upload multiple files | `multipart/form-data` (files[]) | 202 Accepted + batch status |
| `/ingest/job/{job_id}` | GET | Query job status | None | 200 OK + job details |
| `/documents/{document_id}` | GET | Get document metadata | None | 200 OK + document |
| `/documents` | GET | List documents (paginated) | Query params | 200 OK + document list |
| `/health` | GET | Service health check | None | 200 OK / 503 Unavailable |
| `/metrics` | GET | Ingestion statistics | None | 200 OK + metrics |

### Authentication

**MVP**: No authentication (internal service)
**Future**: Add API key or JWT authentication

### Rate Limiting

**MVP**: No rate limiting
**Future**: 100 requests/minute per IP

## Usage Examples

### 1. Upload Single File

```bash
curl -X POST http://localhost:8000/api/v1/ingest/file \
  -F "file=@robotics-chapter-1.pdf"
```

**Response (202 Accepted)**:
```json
{
  "job_id": "b2c3d4e5-6789-01ab-cdef-2345678901bc",
  "document_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "status": "pending",
  "message": "Document accepted for processing"
}
```

### 2. Ingest from URL

```bash
curl -X POST http://localhost:8000/api/v1/ingest/url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/robotics-chapter-1.html"}'
```

**Response (202 Accepted)**:
```json
{
  "job_id": "c3d4e5f6-7890-12ab-cdef-3456789012cd",
  "document_id": "b2c3d4e5-6789-01ab-cdef-2345678901bc",
  "status": "pending",
  "message": "Document accepted for processing"
}
```

### 3. Batch Upload

```bash
curl -X POST http://localhost:8000/api/v1/ingest/batch \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.txt" \
  -F "files=@doc3.docx"
```

**Response (202 Accepted)**:
```json
{
  "job_id": "d4e5f6g7-8901-23ab-cdef-4567890123de",
  "total_files": 3,
  "accepted_files": 3,
  "rejected_files": 0,
  "document_ids": [
    "e5f6g7h8-9012-34ab-cdef-5678901234ef",
    "f6g7h8i9-0123-45ab-cdef-6789012345f0",
    "g7h8i9j0-1234-56ab-cdef-7890123456g1"
  ],
  "errors": [],
  "status": "pending"
}
```

### 4. Check Job Status

```bash
curl http://localhost:8000/api/v1/ingest/job/b2c3d4e5-6789-01ab-cdef-2345678901bc
```

**Response (200 OK)**:
```json
{
  "job_id": "b2c3d4e5-6789-01ab-cdef-2345678901bc",
  "job_type": "single",
  "status": "completed",
  "total_documents": 1,
  "documents_processed": 1,
  "documents_failed": 0,
  "started_at": "2025-12-17T11:00:00Z",
  "completed_at": "2025-12-17T11:00:15Z",
  "error_logs": [],
  "document_ids": ["a1b2c3d4-5678-90ab-cdef-1234567890ab"]
}
```

### 5. Get Document Metadata

```bash
curl http://localhost:8000/api/v1/documents/a1b2c3d4-5678-90ab-cdef-1234567890ab
```

**Response (200 OK)**:
```json
{
  "document_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "filename": "robotics-chapter-1.pdf",
  "content_type": "pdf",
  "content_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "file_size_bytes": 2457600,
  "source_url": null,
  "upload_date": "2025-12-17T11:00:00Z",
  "processing_status": "completed",
  "processing_started_at": "2025-12-17T11:00:01Z",
  "processing_completed_at": "2025-12-17T11:00:15Z",
  "chunk_count": 42,
  "error_message": null,
  "ingestion_job_id": "b2c3d4e5-6789-01ab-cdef-2345678901bc"
}
```

### 6. List Documents (Paginated)

```bash
curl "http://localhost:8000/api/v1/documents?limit=10&offset=0&status=completed"
```

**Response (200 OK)**:
```json
{
  "total": 152,
  "limit": 10,
  "offset": 0,
  "documents": [
    { /* document object */ },
    { /* document object */ },
    // ... 8 more
  ]
}
```

### 7. Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Response (200 OK)**:
```json
{
  "status": "healthy",
  "dependencies": {
    "qdrant": {
      "status": "up",
      "latency_ms": 12,
      "error": null
    },
    "cohere": {
      "status": "up",
      "latency_ms": 245,
      "error": null
    }
  }
}
```

### 8. Get Metrics

```bash
curl http://localhost:8000/api/v1/metrics
```

**Response (200 OK)**:
```json
{
  "total_documents": 152,
  "total_chunks": 6384,
  "documents_by_status": {
    "pending": 2,
    "processing": 1,
    "completed": 147,
    "failed": 2
  },
  "avg_processing_time_seconds": 12.3,
  "avg_chunks_per_document": 42.0
}
```

## Error Responses

### 400 Bad Request - Invalid File Type

```json
{
  "error": "INVALID_FILE_TYPE",
  "message": "Unsupported file type: .exe. Allowed: .pdf, .txt, .docx, .html"
}
```

### 409 Conflict - Duplicate Document

```json
{
  "error": "DUPLICATE_DOCUMENT",
  "message": "Document with identical content already exists",
  "details": {
    "existing_document_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab"
  }
}
```

### 413 Payload Too Large

```json
{
  "error": "FILE_TOO_LARGE",
  "message": "File exceeds 500MB limit: 612.3MB"
}
```

### 404 Not Found

```json
{
  "error": "NOT_FOUND",
  "message": "Document not found: a1b2c3d4-5678-90ab-cdef-1234567890ab"
}
```

### 500 Internal Server Error

```json
{
  "error": "INTERNAL_ERROR",
  "message": "An unexpected error occurred during processing"
}
```

## Contract Testing

### Prerequisites

```bash
pip install pytest pytest-asyncio httpx
```

### Test Structure

```python
# tests/contract/test_ingestion_api.py

import pytest
from fastapi.testclient import TestClient
from backend.src.main import app

client = TestClient(app)

def test_ingest_file_contract():
    """Test /ingest/file endpoint matches OpenAPI contract."""
    with open("test_document.pdf", "rb") as f:
        response = client.post("/api/v1/ingest/file", files={"file": f})

    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "document_id" in data
    assert "status" in data
    assert data["status"] in ["pending", "processing"]

def test_ingest_invalid_file_type():
    """Test rejection of unsupported file types."""
    with open("malicious.exe", "rb") as f:
        response = client.post("/api/v1/ingest/file", files={"file": f})

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "INVALID_FILE_TYPE"

# ... more contract tests
```

### Running Tests

```bash
pytest tests/contract/test_ingestion_api.py -v
```

## Implementation Checklist

- [ ] FastAPI app with `/api/v1` prefix
- [ ] Pydantic request/response models matching OpenAPI schemas
- [ ] File upload validation (size, type, MIME)
- [ ] Duplicate detection via content hash
- [ ] Job tracking with UUIDs
- [ ] Error responses with structured error codes
- [ ] Health check endpoint with dependency status
- [ ] Metrics endpoint with aggregated stats
- [ ] OpenAPI docs auto-generated at `/docs`
- [ ] Contract tests covering all endpoints

## OpenAPI Validation

### Validate Spec

```bash
# Install OpenAPI validator
npm install -g @stoplight/spectral-cli

# Validate spec
spectral lint ingestion-api.yaml
```

### Generate Client SDK (Optional)

```bash
# Install OpenAPI Generator
npm install -g @openapitools/openapi-generator-cli

# Generate Python client
openapi-generator-cli generate \
  -i ingestion-api.yaml \
  -g python \
  -o ./client-sdk
```

## Next Steps

1. ✅ Contracts defined in OpenAPI 3.0 format
2. ⏭️ Implement FastAPI endpoints matching these contracts
3. ⏭️ Write contract tests to validate implementation
4. ⏭️ Generate interactive API docs at `/docs` using FastAPI auto-docs
5. ⏭️ Add authentication and rate limiting (post-MVP)

## References

- [OpenAPI 3.0 Specification](https://swagger.io/specification/)
- [FastAPI OpenAPI Integration](https://fastapi.tiangolo.com/tutorial/metadata/)
- [Pydantic Models](https://docs.pydantic.dev/)
- [HTTP Status Codes](https://httpstatuses.com/)
