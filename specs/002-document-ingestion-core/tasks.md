# Implementation Tasks: Document Ingestion Core System

**Feature**: 002-document-ingestion-core
**Created**: 2025-12-17
**Plan**: [plan.md](plan.md)
**Spec**: [spec.md](spec.md)

## Overview

This task breakdown follows Test-Driven Development (TDD) principles per constitution requirement. Tasks are organized by user story priority (P1 → P2 → P3) to enable independent, incremental delivery.

**Total Tasks**: 62
**MVP Scope**: Phase 3 (User Story 1 + 3) = 22 tasks
**Estimated Duration**: 3-5 days for MVP, 8-12 days for complete feature

## Dependencies & Execution Order

**Phase Completion Order** (sequential):
1. Phase 1: Setup (required for all)
2. Phase 2: Foundational (required for all user stories)
3. Phase 3: US1 + US3 (P1) - **MVP DELIVERABLE**
4. Phase 4: US4 (P2) - Independent, can run in parallel with Phase 5
5. Phase 5: US2 (P2) - Independent, can run in parallel with Phase 4
6. Phase 6: US5 (P3) - Depends on Phase 3 completion
7. Phase 7: Polish - Runs after all user stories complete

**Parallel Opportunities**:
- Phase 4 (Metadata) and Phase 5 (Batch) are independent
- Within each phase, tasks marked [P] can run in parallel
- Test tasks within a phase can run in parallel

---

## Phase 1: Setup & Project Initialization

**Goal**: Initialize project structure, dependencies, and configuration

**Duration**: ~2 hours

### Tasks

- [X] T001 Create backend directory structure per plan.md (backend/src/{models,services,api,utils}, backend/tests/{contract,integration,unit})
- [X] T002 Create backend/requirements.txt with pinned dependencies (FastAPI==0.104.0, qdrant-client==1.6.0, cohere==4.0.0, beautifulsoup4==4.11.0, python-dotenv==0.19.0, pydantic==2.0.0, requests==2.28.0, PyPDF2==3.0.0, python-docx==0.8.11, python-magic==0.4.27, pytest==7.4.0, pytest-asyncio, pytest-cov)
- [X] T003 [P] Create backend/.env.example with template variables (QDRANT_URL, QDRANT_API_KEY, COHERE_API_KEY, OPENAI_API_KEY, SITEMAP_URL, LOG_LEVEL)
- [X] T004 [P] Create backend/src/__init__.py and all module __init__.py files
- [X] T005 [P] Create .gitignore with Python patterns (__pycache__/, *.pyc, .venv/, venv/, dist/, *.egg-info/, .env, *.log)
- [X] T006 Configure pytest in backend/pytest.ini with coverage settings (minimum 80% per constitution)
- [X] T007 Create backend/README.md with setup instructions referencing quickstart.md

**Acceptance**: Project structure matches plan.md, all dependencies installable via `pip install -r requirements.txt`, pytest runs without errors

---

## Phase 2: Foundational Infrastructure

**Goal**: Implement shared utilities and configuration needed by all user stories

**Duration**: ~3 hours

### Tasks

- [X] T008 Implement structured logging configuration in backend/src/utils/logging_config.py (JSON format, request IDs, log levels per constitution Principle VI)
- [X] T009 [P] Implement content hashing utility in backend/src/utils/hashing.py (SHA-256 hash generation with text normalization per research.md)
- [X] T010 [P] Write unit tests for hashing utility in backend/tests/unit/test_hashing.py (test normalization, collision resistance, performance <0.1s per doc)
- [X] T011 Implement Qdrant client initialization in backend/src/services/storage.py (connection pooling, collection schema creation per data-model.md)
- [ ] T012 [P] Write integration tests for Qdrant in backend/tests/integration/test_qdrant_integration.py (mock Qdrant responses, test connection, collection creation, batch upsert)
- [X] T013 Implement Cohere client initialization in backend/src/services/storage.py (embedding generation with embed-english-v3.0 model per research.md)
- [X] T015 Create Pydantic base schemas in backend/src/api/schemas.py (ErrorResponse, HealthStatus, DependencyStatus per contracts/ingestion-api.yaml)
- [X] T016 Implement FastAPI app initialization in backend/src/main.py (CORS middleware, error handlers, lifespan events for Qdrant/Cohere clients)
- [X] T017 [US1] Write unit tests for Document model in backend/tests/unit/test_document_model.py (test field validation, status transitions, content_hash uniqueness per data-model.md)
- [X] T018 [US1] Implement Document model in backend/src/models/document.py (Pydantic model with 12 fields per data-model.md, validation rules)
- [X] T019 [P] [US3] Write unit tests for Chunk model in backend/tests/unit/test_chunk_model.py (test field validation, char_count=len(text_content), chunk_index uniqueness per document)
- [X] T020 [P] [US3] Implement Chunk model in backend/src/models/chunk.py (Pydantic model with 10 fields per data-model.md, embedding_vector validation)
- [X] T021 [US1] Write unit tests for file validation in backend/tests/unit/test_validation.py (test size limits 0<size≤500MB, extension validation .pdf/.txt/.docx/.html, MIME type checks, error messages per research.md)
- [X] T022 [US1] Implement file validation service in backend/src/services/validation.py (layered validation: size → extension → MIME per research.md Decision 6)
- [X] T023 [US3] Write unit tests for text extraction in backend/tests/unit/test_extraction.py (test PDF extraction with PyPDF2, DOCX with python-docx, HTML with BeautifulSoup4, TXT pass-through, accuracy ≥95% per SC-002)
- [X] T024 [US3] Implement extraction service in backend/src/services/extraction.py (format-specific extractors per research.md Decision 1, HTML sanitization removing scripts/styles)
- [X] T025 [US3] Write unit tests for chunking in backend/tests/unit/test_chunking.py (test recursive splitter, 500≤chars≤2000, 100-char overlap, sentence boundary preservation per research.md Decision 2)
- [X] T026 [US3] Implement chunking service in backend/src/services/chunking.py (recursive character splitter with paragraph→sentence→char hierarchy, overlap handling)
- [X] T027 [US1] Write unit tests for ingestion orchestration in backend/tests/unit/test_ingestion.py (test end-to-end flow: validate→extract→chunk→embed→store, duplicate detection via content_hash, error handling per FR-008)
- [X] T028 [US1] Implement ingestion service in backend/src/services/ingestion.py (coordinate validation→extraction→chunking→embedding→storage, atomic operations per constitution Principle I)
- [X] T029 [US3] Implement Qdrant storage operations in backend/src/services/storage.py (batch upsert chunks, store denormalized document metadata per data-model.md, handle duplicates returning 409)
- [X] T030 [P] [US3] Write integration tests for storage in backend/tests/integration/test_storage.py (test chunk upsert, metadata denormalization, duplicate rejection, batch performance >100 chunks/sec)
- [X] T031 [US1] Write contract tests for /ingest/file endpoint in backend/tests/contract/test_ingestion_api.py (test request validation, 202 response, job_id/document_id returned, 400 for invalid types, 413 for >500MB, 409 for duplicates per contracts/ingestion-api.yaml)
- [X] T032 [US1] Implement POST /api/v1/ingest/file endpoint in backend/src/api/endpoints.py (multipart file upload, trigger ingestion, return IngestionResponse schema)
- [X] T033 [P] [US1] Implement GET /api/v1/ingest/job/{job_id} endpoint in backend/src/api/endpoints.py (query job status, return JobStatus schema)
- [X] T034 [P] [US1] Implement GET /api/v1/documents/{document_id} endpoint in backend/src/api/endpoints.py (query document metadata, return Document schema)
- [X] T035 [US1] Implement GET /api/v1/health endpoint in backend/src/api/endpoints.py (check Qdrant/Cohere connectivity, return HealthStatus schema)
- [X] T036 [US1] Implement GET /api/v1/metrics endpoint in backend/src/api/endpoints.py (aggregate stats from Qdrant: total_documents, total_chunks, avg_processing_time)
- [X] T037 [US1] Write end-to-end test in backend/tests/integration/test_e2e_single_ingestion.py (upload test PDF → verify chunks in Qdrant → verify embeddings dimension=1024 → verify metadata correctness → verify processing <30s for 100 pages per SC-003)
- [X] T038 [US3] Run full test suite and verify ≥80% coverage per constitution (pytest --cov=backend/src --cov-report=html)
- [X] T043 [P] [US2] Write unit tests for IngestionJob model in backend/tests/unit/test_ingestion_job_model.py (test field validation, status transitions pending→processing→completed/partial_success/failed, documents_processed+documents_failed≤total_documents per data-model.md)
- [X] T044 [US2] Implement IngestionJob model in backend/src/models/ingestion_job.py (Pydantic model with 8 fields, status enum, error_logs array)
- [X] T045 [US2] Write unit tests for batch ingestion in backend/tests/unit/test_batch_ingestion.py (test sequential processing, error isolation per FR-008 graceful degradation, partial success handling per US2 acceptance scenario 2)
- [X] T046 [US2] Implement batch ingestion logic in backend/src/services/ingestion.py (process_batch method, max 100 docs per FR-010, sequential processing with error isolation, create IngestionJob tracker)
- [X] T047 [US2] Write contract tests for /ingest/batch endpoint in backend/tests/contract/test_batch_api.py (test multipart files array, max 100 files, 202 response with BatchIngestionResponse, rejected files in errors array)
- [X] T048 [US2] Implement POST /api/v1/ingest/batch endpoint in backend/src/api/endpoints.py (accept files array, trigger batch ingestion, return batch status)
- [X] T049 [US2] Write integration test in backend/tests/integration/test_batch_e2e.py (upload 50 documents batch → verify throughput ≥50 docs/hour per NFR, verify SC-004 batch success)
- [X] T050 [P] [US5] Write unit tests for URL validation in backend/tests/unit/test_url_validation.py (test scheme whitelist http/https only, private IP blocking per research.md Decision 5, redirect validation, timeout 30s, malicious URL rejection)
- [X] T051 [US5] Implement URL validation and fetching in backend/src/services/validation.py (SSRF prevention: whitelist schemes, block private IPs 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16, manual redirect handling)
- [X] T052 [US5] Write contract tests for /ingest/url endpoint in backend/tests/contract/test_url_api.py (test JSON request with url field, 202 response, 400 for invalid/unreachable URLs per US5 acceptance scenario 3)
- [X] T053 [US5] Implement POST /api/v1/ingest/url endpoint in backend/src/api/endpoints.py (validate URL, fetch content, determine type HTML vs PDF, trigger ingestion with source_url metadata)
- [X] T054 [US5] Write integration test in backend/tests/integration/test_url_e2e.py (test HTML page ingestion, PDF file download, redirect handling, SSRF protection blocks private IPs)
- [X] T055 [P] Implement GET /api/v1/documents endpoint with pagination in backend/src/api/endpoints.py (query params limit/offset/status, return DocumentList schema, max 100 per page per constitution)
- [X] T056 [P] Add request ID tracking to logging in backend/src/utils/logging_config.py (generate UUID per request, include in all log entries for traceability per constitution Principle VI)
- [X] T057 [P] Implement error aggregation metrics in backend/src/api/endpoints.py (track error types/frequencies in /metrics endpoint)
- [X] T058 Performance optimization: Profile chunking service and optimize for >1MB/s per research.md benchmark
- [X] T059 Performance optimization: Benchmark Qdrant batch upsert and verify >100 chunks/sec per research.md)
- [X] T060 Security audit: Run pip-audit on dependencies, fix CVEs per constitution Principle IV
- [X] T061 Documentation: Generate OpenAPI docs at /docs endpoint (FastAPI auto-docs)
- [X] T062 Documentation: Update backend/README.md with API usage examples from quickstart.md
- [X] T014 [P] Write integration tests for Cohere in backend/tests/integration/test_cohere_integration.py (mock Cohere API, test embedding dimension=1024, error handling)

**Acceptance**: All foundational services initialize successfully, tests pass, logging outputs JSON format, Qdrant/Cohere clients connect

---

## Phase 3: User Story 1 + 3 (P1) - Single Document Ingestion with Chunking

**Goal**: Implement MVP - ingest single document, extract text, chunk, embed, store

**Priority**: P1 (foundational capability)

**Independent Test**: Upload single PDF/TXT/DOCX file → verify document processed → verify chunks stored in Qdrant with embeddings → verify metadata correct

**Duration**: ~1.5 days (12 hours)

### US1+US3: Data Models

- [X] T017 [US1] Write unit tests for Document model in backend/tests/unit/test_document_model.py (test field validation, status transitions, content_hash uniqueness per data-model.md)
- [X] T018 [US1] Implement Document model in backend/src/models/document.py (Pydantic model with 12 fields per data-model.md, validation rules)
- [X] T019 [P] [US3] Write unit tests for Chunk model in backend/tests/unit/test_chunk_model.py (test field validation, char_count=len(text_content), chunk_index uniqueness per document)
- [X] T020 [P] [US3] Implement Chunk model in backend/src/models/chunk.py (Pydantic model with 10 fields per data-model.md, embedding_vector validation)

### US1+US3: File Validation

- [X] T021 [US1] Write unit tests for file validation in backend/tests/unit/test_validation.py (test size limits 0<size≤500MB, extension validation .pdf/.txt/.docx/.html, MIME type checks, error messages per research.md)
- [X] T022 [US1] Implement file validation service in backend/src/services/validation.py (layered validation: size → extension → MIME per research.md Decision 6)

### US1+US3: Text Extraction

- [X] T023 [US3] Write unit tests for text extraction in backend/tests/unit/test_extraction.py (test PDF extraction with PyPDF2, DOCX with python-docx, HTML with BeautifulSoup4, TXT pass-through, accuracy ≥95% per SC-002)
- [X] T024 [US3] Implement extraction service in backend/src/services/extraction.py (format-specific extractors per research.md Decision 1, HTML sanitization removing scripts/styles)

### US1+US3: Text Chunking

- [X] T025 [US3] Write unit tests for chunking in backend/tests/unit/test_chunking.py (test recursive splitter, 500≤chars≤2000, 100-char overlap, sentence boundary preservation per research.md Decision 2)
- [X] T026 [US3] Implement chunking service in backend/src/services/chunking.py (recursive character splitter with paragraph→sentence→char hierarchy, overlap handling)

### US1+US3: Ingestion Orchestration

- [X] T027 [US1] Write unit tests for ingestion orchestration in backend/tests/unit/test_ingestion.py (test end-to-end flow: validate→extract→chunk→embed→store, duplicate detection via content_hash, error handling per FR-008)
- [X] T028 [US1] Implement ingestion service in backend/src/services/ingestion.py (coordinate validation→extraction→chunking→embedding→storage, atomic operations per constitution Principle I)

### US1+US3: Storage Operations

- [X] T029 [US3] Implement Qdrant storage operations in backend/src/services/storage.py (batch upsert chunks, store denormalized document metadata per data-model.md, handle duplicates returning 409)
- [X] T030 [P] [US3] Write integration tests for storage in backend/tests/integration/test_storage.py (test chunk upsert, metadata denormalization, duplicate rejection, batch performance >100 chunks/sec)

### US1+US3: API Endpoints

- [X] T031 [US1] Write contract tests for /ingest/file endpoint in backend/tests/contract/test_ingestion_api.py (test request validation, 202 response, job_id/document_id returned, 400 for invalid types, 413 for >500MB, 409 for duplicates per contracts/ingestion-api.yaml)
- [X] T032 [US1] Implement POST /api/v1/ingest/file endpoint in backend/src/api/endpoints.py (multipart file upload, trigger ingestion, return IngestionResponse schema)
- [X] T033 [P] [US1] Implement GET /api/v1/ingest/job/{job_id} endpoint in backend/src/api/endpoints.py (query job status, return JobStatus schema)
- [X] T034 [P] [US1] Implement GET /api/v1/documents/{document_id} endpoint in backend/src/api/endpoints.py (query document metadata, return Document schema)
- [X] T035 [US1] Implement GET /api/v1/health endpoint in backend/src/api/endpoints.py (check Qdrant/Cohere connectivity, return HealthStatus schema)
- [X] T036 [US1] Implement GET /api/v1/metrics endpoint in backend/src/api/endpoints.py (aggregate stats from Qdrant: total_documents, total_chunks, avg_processing_time)

### US1+US3: End-to-End Testing

- [X] T037 [US1] Write end-to-end test in backend/tests/integration/test_e2e_single_ingestion.py (upload test PDF → verify chunks in Qdrant → verify embeddings dimension=1024 → verify metadata correctness → verify processing <30s for 100 pages per SC-003)
- [X] T038 [US3] Run full test suite and verify ≥80% coverage per constitution (pytest --cov=backend/src --cov-report=html)

**MVP Deliverable**: Single document ingestion working end-to-end with FastAPI endpoints, tests passing, ≥80% coverage

---

## Phase 4: User Story 4 (P2) - Metadata Extraction and Storage

**Goal**: Extract and store rich metadata (title, author, date) beyond basic filename/size

**Priority**: P2 (enhancement for discoverability)

**Independent Test**: Ingest PDF with embedded metadata → verify author/title extracted → ingest TXT without metadata → verify filename/date generated → ingest from URL → verify source URL stored

**Duration**: ~4 hours

### Tasks

- [X] T039 [P] [US4] Write unit tests for metadata extraction in backend/tests/unit/test_metadata_extraction.py (test PDF metadata extraction with PyPDF2.PdfReader.metadata, DOCX with python-docx core properties, HTML meta tags, TXT fallback to filename/date/size)
- [X] T040 [US4] Implement metadata extraction in backend/src/services/extraction.py (extend extractors to capture title/author/date per US4 acceptance scenarios, handle missing metadata gracefully)
- [X] T041 [US4] Update Document model in backend/src/models/document.py to add optional metadata fields (title, author, creation_date, update document storage to persist these fields)
- [X] T042 [US4] Write integration test in backend/tests/integration/test_metadata_e2e.py (verify metadata flows from extraction → storage → retrieval for PDF/DOCX/HTML/TXT)

**Acceptance**: Metadata extracted and stored per US4 acceptance scenarios, tests pass

---

## Phase 5: User Story 2 (P2) - Batch Document Ingestion

**Goal**: Process multiple documents in a single batch request with error isolation

**Priority**: P2 (operational efficiency)

**Independent Test**: Upload batch of 10 files (8 valid, 2 invalid) → verify 8 processed → verify 2 rejected with error logs → verify partial success status

**Duration**: ~6 hours

### Tasks

- [X] T043 [P] [US2] Write unit tests for IngestionJob model in backend/tests/unit/test_ingestion_job_model.py (test field validation, status transitions pending→processing→completed/partial_success/failed, documents_processed+documents_failed≤total_documents per data-model.md)
- [X] T044 [US2] Implement IngestionJob model in backend/src/models/ingestion_job.py (Pydantic model with 8 fields, status enum, error_logs array)
- [X] T045 [US2] Write unit tests for batch ingestion in backend/tests/unit/test_batch_ingestion.py (test sequential processing, error isolation per FR-008 graceful degradation, partial success handling per US2 acceptance scenario 2)
- [X] T046 [US2] Implement batch ingestion logic in backend/src/services/ingestion.py (process_batch method, max 100 docs per FR-010, sequential processing with error isolation, create IngestionJob tracker)
- [X] T047 [US2] Write contract tests for /ingest/batch endpoint in backend/tests/contract/test_batch_api.py (test multipart files array, max 100 files, 202 response with BatchIngestionResponse, rejected files in errors array)
- [X] T048 [US2] Implement POST /api/v1/ingest/batch endpoint in backend/src/api/endpoints.py (accept files array, trigger batch ingestion, return batch status)
- [X] T049 [US2] Write integration test in backend/tests/integration/test_batch_e2e.py (upload 50 documents batch → verify throughput ≥50 docs/hour per NFR, verify SC-004 batch success)

**Acceptance**: Batch ingestion handles 50 documents without failures, error isolation works, tests pass

---

## Phase 6: User Story 5 (P3) - URL-Based Document Ingestion

**Goal**: Ingest content from web URLs with SSRF protection

**Priority**: P3 (convenience feature)

**Independent Test**: Provide static HTML URL → verify content fetched and processed → provide PDF URL → verify file downloaded and ingested → provide invalid URL → verify error message

**Duration**: ~4 hours

### Tasks

- [X] T050 [P] [US5] Write unit tests for URL validation in backend/tests/unit/test_url_validation.py (test scheme whitelist http/https only, private IP blocking per research.md Decision 5, redirect validation, timeout 30s, malicious URL rejection)
- [X] T051 [US5] Implement URL validation and fetching in backend/src/services/validation.py (SSRF prevention: whitelist schemes, block private IPs 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16, manual redirect handling)
- [X] T052 [US5] Write contract tests for /ingest/url endpoint in backend/tests/contract/test_url_api.py (test JSON request with url field, 202 response, 400 for invalid/unreachable URLs per US5 acceptance scenario 3)
- [X] T053 [US5] Implement POST /api/v1/ingest/url endpoint in backend/src/api/endpoints.py (validate URL, fetch content, determine type HTML vs PDF, trigger ingestion with source_url metadata)
- [X] T054 [US5] Write integration test in backend/tests/integration/test_url_e2e.py (test HTML page ingestion, PDF file download, redirect handling, SSRF protection blocks private IPs)

**Acceptance**: URL ingestion works for HTML and PDF, SSRF protection verified, tests pass

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Finalize documentation, optimize performance, ensure production readiness

**Duration**: ~4 hours

### Tasks

- [X] T055 [P] Implement GET /api/v1/documents endpoint with pagination in backend/src/api/endpoints.py (query params limit/offset/status, return DocumentList schema, max 100 per page per constitution)
- [X] T056 [P] Add request ID tracking to logging in backend/src/utils/logging_config.py (generate UUID per request, include in all log entries for traceability per constitution Principle VI)
- [X] T057 [P] Implement error aggregation metrics in backend/src/api/endpoints.py (track error types/frequencies in /metrics endpoint)
- [X] T058 Performance optimization: Profile chunking service and optimize for >1MB/s per research.md benchmark
- [X] T059 Performance optimization: Benchmark Qdrant batch upsert and verify >100 chunks/sec per research.md
- [X] T060 Security audit: Run pip-audit on dependencies, fix CVEs per constitution Principle IV
- [X] T061 Documentation: Generate OpenAPI docs at /docs endpoint (FastAPI auto-docs)
- [X] T062 Documentation: Update backend/README.md with API usage examples from quickstart.md

**Acceptance**: All endpoints documented, performance benchmarks met, security audit clean, production ready

---

## Implementation Strategy

### MVP First (Phase 3 Only)

**Recommended**: Implement Phase 3 (US1+US3) first to get a working MVP in 1.5 days

**MVP Deliverables**:
- Single document ingestion via API
- Text extraction from PDF/TXT/DOCX/HTML
- Chunking with boundary preservation
- Vector embeddings stored in Qdrant
- Health and metrics endpoints
- ≥80% test coverage

**MVP Validation**:
```bash
# Start FastAPI server
uvicorn backend.src.main:app --reload

# Upload document
curl -X POST http://localhost:8000/api/v1/ingest/file -F "file=@test.pdf"

# Check status
curl http://localhost:8000/api/v1/ingest/job/{job_id}

# Verify health
curl http://localhost:8000/api/v1/health
```

### Incremental Delivery

After MVP (Phase 3), deliver in priority order:

1. **Phase 4** (Metadata) - Independent, can parallelize with Phase 5
2. **Phase 5** (Batch) - Independent, can parallelize with Phase 4
3. **Phase 6** (URL) - Depends on Phase 3
4. **Phase 7** (Polish) - Final refinement

### Parallel Execution Examples

**Within Phase 3** (examples):
```bash
# Run test tasks in parallel
pytest backend/tests/unit/test_document_model.py & \
pytest backend/tests/unit/test_chunk_model.py & \
pytest backend/tests/unit/test_validation.py & \
wait

# Implement models in parallel (different files)
# T018: Implement Document model
# T020: Implement Chunk model (parallel with T018)
```

**Cross-Phase Parallelization**:
```bash
# After Phase 3 complete, run Phase 4 and Phase 5 in parallel
# Team member A: Implement Phase 4 (Metadata)
# Team member B: Implement Phase 5 (Batch)
```

---

## Task Format Validation

✅ **All 62 tasks follow checklist format**:
- Checkbox: `- [ ]`
- Task ID: T001-T062 (sequential)
- [P] marker: Present for parallelizable tasks
- [Story] label: Present for user story phase tasks (US1-US5)
- File paths: Included in descriptions
- Clear acceptance criteria per phase

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 62 |
| **Setup Tasks** | 7 (Phase 1) |
| **Foundational Tasks** | 9 (Phase 2) |
| **MVP Tasks (US1+US3)** | 22 (Phase 3) |
| **US4 Tasks** | 4 (Phase 4) |
| **US2 Tasks** | 7 (Phase 5) |
| **US5 Tasks** | 5 (Phase 6) |
| **Polish Tasks** | 8 (Phase 7) |
| **Parallel Opportunities** | 18 tasks marked [P] |
| **Test Tasks** | 26 (42% of total, per TDD) |
| **Estimated Duration** | 3-5 days MVP, 8-12 days complete |

**Next Step**: Run `/sp.implement` to execute tasks in TDD order (Red-Green-Refactor cycle)
