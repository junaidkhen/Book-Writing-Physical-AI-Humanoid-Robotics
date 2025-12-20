# Feature Specification: Document Ingestion Core System

**Feature Branch**: `002-document-ingestion-core`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "- Frontend UI for ingestion status
- Retrieval or answer generation logic (covered in later specs)
- Agent, chatbot, or FastAPI backend
- Browser-based scraping of dynamic JS content"

## Clarifications

### Session 2025-12-16

- Q: Sitemap URL Configuration - Should the sitemap URL be added to .env with the exact variable name SITEMAP_URL for automatic URL discovery? → A: Add `SITEMAP_URL="https://book-writing-physical-ai-humanoid-r.vercel.app/sitemap.xml"` to `.env` file (recommended for automatic URL discovery)
- Q: Qdrant Data Visibility Issue - Should we run the ingestion pipeline first to create the collection and populate it with data? → A: Run the ingestion pipeline now to create and populate the "documents" collection (ensures data exists before checking UI)
- Q: Implementation Scope - What is the complete workflow to implement data on web using Cohere? → A: Run full workflow: update .env → run ingestion → start FastAPI server → test endpoints (complete end-to-end setup)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ingest Single Static Document (Priority: P1)

A content manager needs to add a new document to the knowledge base for processing and indexing.

**Why this priority**: This is the foundational capability - without the ability to ingest at least one document, no other features can function. This represents the absolute minimum viable product.

**Independent Test**: Can be fully tested by providing a single document file, triggering ingestion, and verifying the document is successfully processed and stored. Delivers immediate value by enabling basic document addition to the system.

**Acceptance Scenarios**:

1. **Given** a valid document file (PDF, TXT, or DOCX), **When** the ingestion process is triggered, **Then** the document is successfully parsed and stored with metadata
2. **Given** an unsupported file format, **When** ingestion is attempted, **Then** the system rejects the file with a clear error message
3. **Given** a corrupted document file, **When** ingestion is attempted, **Then** the system handles the error gracefully and logs the failure

---

### User Story 2 - Batch Document Ingestion (Priority: P2)

A content manager needs to upload multiple documents at once to populate the knowledge base efficiently.

**Why this priority**: Significantly improves operational efficiency but the system can function with single-document ingestion. This is an enhancement that makes the system practical for real-world use.

**Independent Test**: Can be tested by providing a collection of documents (e.g., 10-100 files), triggering batch ingestion, and verifying all valid documents are processed. Delivers value by reducing manual effort for bulk operations.

**Acceptance Scenarios**:

1. **Given** a directory containing multiple valid documents, **When** batch ingestion is triggered, **Then** all documents are processed sequentially or in parallel
2. **Given** a batch containing some invalid files, **When** batch ingestion runs, **Then** valid files are processed while invalid files are logged and skipped
3. **Given** a batch ingestion in progress, **When** the process is interrupted, **Then** already-processed documents remain stored and unprocessed documents can be retried

---

### User Story 3 - Automatic Text Extraction and Chunking (Priority: P1)

The system needs to break down documents into manageable, semantically meaningful chunks for downstream processing.

**Why this priority**: Core requirement for making documents usable - without chunking, documents cannot be effectively processed for retrieval or analysis. This is essential infrastructure.

**Independent Test**: Can be tested by ingesting a document and verifying it's split into appropriate chunks with preserved context. Delivers value by making document content accessible for processing.

**Acceptance Scenarios**:

1. **Given** a document with clear section boundaries, **When** chunking is applied, **Then** the document is split at logical boundaries (paragraphs, sections, pages)
2. **Given** a very long document (500+ pages), **When** chunking is applied, **Then** the system handles it without memory issues and maintains context
3. **Given** a document with mixed content types (text, tables, images), **When** text extraction occurs, **Then** text content is extracted while preserving semantic structure

---

### User Story 4 - Metadata Extraction and Storage (Priority: P2)

The system needs to extract and store document metadata (title, author, date, source) for organization and filtering.

**Why this priority**: Enhances discoverability and organization but isn't required for basic ingestion. Adds significant value for managing large document collections.

**Independent Test**: Can be tested by ingesting documents with known metadata and verifying the metadata is correctly extracted and stored. Delivers value by enabling document organization and search filtering.

**Acceptance Scenarios**:

1. **Given** a document with embedded metadata (PDF with author/title), **When** ingestion occurs, **Then** metadata is extracted and stored alongside the document
2. **Given** a plain text file with no metadata, **When** ingestion occurs, **Then** system generates basic metadata (filename, date added, file size)
3. **Given** a document from a URL source, **When** ingestion occurs, **Then** the source URL and retrieval timestamp are stored as metadata

---

### User Story 5 - URL-Based Document Ingestion (Priority: P3)

A user needs to ingest content from a web URL without manual download.

**Why this priority**: Convenience feature that streamlines workflow but isn't essential - users can manually download and ingest. Adds value for automated workflows.

**Independent Test**: Can be tested by providing a URL to static content, triggering ingestion, and verifying the content is fetched and processed. Delivers value by automating the download-then-ingest workflow.

**Acceptance Scenarios**:

1. **Given** a URL pointing to a static HTML page, **When** URL-based ingestion is triggered, **Then** the page content is fetched and text is extracted
2. **Given** a URL pointing to a PDF file, **When** URL-based ingestion is triggered, **Then** the file is downloaded and processed like a local file
3. **Given** an invalid or unreachable URL, **When** ingestion is attempted, **Then** the system returns a clear error message

---

### Edge Cases

- What happens when a document is empty or contains no extractable text?
- How does the system handle extremely large files (>1GB)?
- What happens if the same document is ingested multiple times?
- How does the system handle documents with non-UTF-8 encodings?
- What happens when storage space is exhausted during ingestion?
- How are documents with password protection handled?
- What happens if chunking fails midway through a document?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept document files in at least these formats: PDF, TXT, DOCX, HTML
- **FR-002**: System MUST extract text content from uploaded documents with at least 95% accuracy for standard documents
- **FR-003**: System MUST chunk documents into segments between 500-2000 characters, preserving sentence boundaries
- **FR-004**: System MUST store both original documents and processed chunks with associations
- **FR-005**: System MUST extract and store basic metadata including filename, file size, upload timestamp, and content type
- **FR-006**: System MUST detect and reject duplicate documents based on content hash
- **FR-007**: System MUST validate file formats before processing and reject unsupported types with clear error messages
- **FR-008**: System MUST handle ingestion failures gracefully without corrupting existing data
- **FR-009**: System MUST support ingestion from file uploads and direct URL inputs
- **FR-013**: System MUST support automatic URL discovery via SITEMAP_URL environment variable pointing to sitemap.xml
- **FR-010**: System MUST process batch uploads sequentially with a maximum of 100 documents per batch
- **FR-011**: System MUST preserve document structure during chunking including headings, lists, and paragraph boundaries to maintain context
- **FR-012**: System MUST log all ingestion attempts with status (success/failure) and error details for failures

### Key Entities

- **Document**: Represents an ingested file with original content, metadata (filename, size, upload date, content type, source URL if applicable), processing status, and associated chunks
- **Chunk**: A segment of text extracted from a document with chunk text content, position in original document, character count, parent document reference, and extraction timestamp
- **IngestionJob**: Tracks the processing of one or more documents with job ID, documents in batch, start/end timestamps, overall status, and error logs

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: System successfully ingests and processes at least 95% of valid document formats without errors
- **SC-002**: Text extraction achieves at least 95% accuracy compared to manual review for standard documents
- **SC-003**: System processes a single document (up to 100 pages) in under 30 seconds
- **SC-004**: System handles batch uploads of 50 documents without failures or data corruption
- **SC-005**: No document data is lost or corrupted during the ingestion process (100% data integrity)
- **SC-006**: System correctly identifies and rejects duplicate documents 100% of the time based on content hash
- **SC-007**: All ingestion failures are logged with sufficient detail to diagnose the issue

## Scope

### In Scope

- Document file ingestion from local uploads
- Document ingestion from static URLs (direct file links, static HTML pages)
- Text extraction from supported document formats (PDF, TXT, DOCX, HTML)
- Document chunking into semantically meaningful segments
- Basic metadata extraction (filename, size, date, type, source)
- Duplicate detection based on content hashing
- Batch processing of multiple documents
- Error handling and logging for ingestion failures
- Storage of original documents and processed chunks

### Out of Scope

- Frontend UI for ingestion status monitoring (covered in separate spec)
- Retrieval or answer generation logic (covered in later specs)
- Agent, chatbot, or FastAPI backend integration (separate concern)
- Browser-based scraping of dynamic JavaScript-rendered content
- Real-time ingestion status updates or progress tracking UI
- Document versioning or update workflows
- User authentication or authorization
- Document deletion or management operations
- Advanced metadata extraction (entities, topics, sentiment)
- Multi-language support (assume English content for MVP)

## Constraints & Assumptions

### Constraints

- Maximum file size per document: 500MB
- Supported document encodings: UTF-8 (other encodings will attempt conversion)
- No real-time processing requirements - batch/asynchronous processing is acceptable
- Static content only - no JavaScript execution for dynamic content

### Assumptions

- Users have appropriate permissions to access and upload documents
- Storage infrastructure has sufficient capacity for document and chunk storage
- Network connectivity is reliable for URL-based ingestion
- Documents contain primarily text content (not heavily image-based)
- Content is primarily in English (for MVP)
- System will run in a server environment with sufficient memory for document processing
- Downstream systems will handle vector embeddings and indexing (not part of ingestion)

## Dependencies

### External Dependencies

- Document parsing libraries (for PDF, DOCX extraction)
- HTTP client for URL-based ingestion
- File storage system (local filesystem or cloud storage)
- Character encoding detection library

### Internal Dependencies

- None - this is a foundational component that other features will depend on

## Non-Functional Requirements

### Performance

- Single document processing (100 pages): < 30 seconds
- Batch processing throughput: At least 50 documents per hour for standard documents
- Memory usage: System should not exceed 2GB RAM for processing a single document

### Reliability

- Data integrity: 100% - no document or chunk data loss during ingestion
- Duplicate detection accuracy: 100% based on content hash
- Graceful degradation: System continues processing remaining documents if one fails in a batch

### Scalability

- System should handle document collections up to 10,000 documents without performance degradation
- Chunk storage should scale linearly with document count

### Security

- Input validation on all uploaded files to prevent malicious file execution
- Content hash verification to detect file tampering
- Sanitization of extracted text to remove potential injection attacks
- Secure handling of URL inputs to prevent SSRF attacks
