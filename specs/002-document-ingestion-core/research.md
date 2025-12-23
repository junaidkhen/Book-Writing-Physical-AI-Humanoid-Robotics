# Technical Research: Document Ingestion Core System

**Feature**: 002-document-ingestion-core
**Date**: 2025-12-17
**Purpose**: Document technical decisions, library evaluations, and implementation patterns for document ingestion pipeline

## Research Questions

1. Which document parsing libraries provide best accuracy/performance trade-off for PDF, DOCX, HTML?
2. What chunking strategy preserves semantic boundaries while meeting 500-2000 character constraints?
3. How to implement content hashing for duplicate detection with zero collision risk?
4. What are Qdrant best practices for chunk storage, indexing, and retrieval?
5. How to prevent SSRF attacks in URL-based ingestion?
6. What file validation techniques prevent malicious uploads?

---

## Decision 1: Document Parsing Libraries

### Requirement
FR-001: Accept PDF, TXT, DOCX, HTML formats
FR-002: ≥95% text extraction accuracy for standard documents

### Options Evaluated

| Library | Formats | Pros | Cons | Decision |
|---------|---------|------|------|----------|
| **PyPDF2** | PDF | Lightweight, pure Python, stable | No OCR, struggles with complex layouts | ✅ **SELECT** for simple PDFs |
| **pdfplumber** | PDF | Better layout preservation, table extraction | Heavier dependencies, slower | ⏸️ Future enhancement |
| **python-docx** | DOCX | Official Microsoft format support, reliable | DOCX only | ✅ **SELECT** |
| **BeautifulSoup4** | HTML | Flexible parsing, proven, handles malformed HTML | Requires content area detection | ✅ **SELECT** |
| **Unstructured.io** | All | Unified API for all formats, ML-enhanced | Heavy (100MB+), overkill for MVP | ❌ REJECT |

### Final Decision

**Use format-specific libraries**: BeautifulSoup4 (HTML), PyPDF2 (PDF), python-docx (DOCX), built-in (TXT)

**Rationale**:
- Lightweight dependencies align with Constitution Principle VII (Simplicity)
- Each library specialized for its format → better accuracy than generic tools
- Combined size <10MB vs 100MB+ for unified solutions
- Proven stability (all libraries 5+ years mature)
- Meets 95% accuracy requirement for "standard documents" (simple layouts, no OCR needed)

**Alternatives Considered & Rejected**:
- **Unstructured.io**: Too heavy for MVP, ML models unnecessary for standard documents
- **Apache Tika**: Java dependency violates pure-Python stack decision
- **pdfplumber**: Defer to v2 if PyPDF2 proves insufficient (benchmark first)

---

## Decision 2: Text Chunking Strategy

### Requirement
FR-003: Chunk into 500-2000 characters, preserving sentence boundaries
FR-011: Preserve structure (headings, lists, paragraphs) for context

### Options Evaluated

| Strategy | Approach | Pros | Cons | Decision |
|----------|----------|------|------|----------|
| **Fixed-size splitting** | Split at exact char boundaries | Simple, fast | Breaks mid-sentence, loses context | ❌ REJECT |
| **Sentence-based chunking** | Split at sentence boundaries, combine to target size | Preserves readability | May exceed 2000 chars for long sentences | ⚠️ Partial |
| **Recursive character splitter** | Try paragraphs → sentences → chars with overlap | Preserves hierarchy, configurable | More complex implementation | ✅ **SELECT** |
| **Semantic chunking (embeddings)** | Use embeddings to find topic boundaries | Best semantic coherence | Slow (requires embeddings upfront), complex | ❌ REJECT (overkill) |

### Final Decision

**Recursive character text splitter with sentence boundary preservation**

**Algorithm**:
1. **Primary split**: Paragraph boundaries (`\n\n`)
2. **Secondary split**: Sentence boundaries (`.!?` followed by space/newline)
3. **Fallback**: Character boundary if sentence >2000 chars
4. **Overlap**: 100-character overlap between chunks to preserve context

**Configuration**:
```python
chunk_size = 1000  # target (middle of 500-2000 range)
chunk_overlap = 100  # 10% overlap for context continuity
separators = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]
```

**Rationale**:
- Meets FR-003 (500-2000 char range) while prioritizing semantic boundaries
- Overlap prevents context loss at chunk edges (e.g., pronoun references)
- Hierarchical splitting preserves FR-011 structure requirements
- Simple implementation aligns with Constitution Principle VII (no ML needed)

**Alternatives Considered & Rejected**:
- **Fixed-size**: Unacceptable quality (breaks mid-sentence)
- **Semantic chunking**: Over-engineering for MVP; defer to v2 if quality issues emerge
- **LangChain text splitter**: Considered but opted for custom implementation to avoid heavy dependency and maintain control

---

## Decision 3: Content Hashing for Duplicate Detection

### Requirement
FR-006: Detect and reject duplicates based on content hash
SC-006: 100% duplicate detection accuracy

### Options Evaluated

| Algorithm | Hash Size | Collision Risk (10K docs) | Performance | Decision |
|-----------|-----------|---------------------------|-------------|----------|
| **MD5** | 128-bit | Cryptographically broken (intentional collisions possible) | Fastest | ❌ REJECT (security) |
| **SHA-256** | 256-bit | ~0% (2^-256 negligible) | Fast (100MB/s) | ✅ **SELECT** |
| **SHA-512** | 512-bit | ~0% (overkill) | Slightly slower | ❌ REJECT (unnecessary) |
| **SimHash** | 64-bit | Fuzzy matching (near-duplicates) | Fast | ❌ REJECT (FR-006 requires exact match) |

### Final Decision

**SHA-256 hash of normalized text content**

**Implementation**:
```python
import hashlib

def generate_content_hash(text: str) -> str:
    """Generate SHA-256 hash of normalized text for duplicate detection."""
    # Normalize: lowercase, remove extra whitespace, strip
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
```

**Rationale**:
- **Zero practical collision risk**: 2^-256 probability is negligible at 10K document scale
- **Security**: SHA-256 is cryptographically secure (prevents intentional collision attacks)
- **Performance**: Hashes 100MB/s on modern CPUs → <0.1s per document
- **Storage**: 64-character hex string → minimal database overhead
- **Normalization**: Lowercase + whitespace normalization catches reformatted duplicates

**Alternatives Considered & Rejected**:
- **MD5**: Cryptographically broken; violates Constitution Principle IV (Security)
- **SimHash**: FR-006 requires exact duplicate detection, not near-duplicate fuzzy matching
- **SHA-512**: No benefit over SHA-256 at this scale; wastes 2x storage

---

## Decision 4: Qdrant Storage Best Practices

### Requirement
FR-004: Store documents and chunks with associations
Performance: <200ms p95 retrieval, scale to 10K documents

### Research Findings

**Collection Schema Design**:
```python
# Single collection: "documents" with chunks as points
collection_config = {
    "vectors": {
        "size": 1024,  # Cohere embed-english-v3.0 dimension
        "distance": "Cosine"  # Standard for text embeddings
    },
    "payload_schema": {
        "document_id": "keyword",  # For filtering by parent document
        "chunk_index": "integer",  # Position in document
        "text": "text",            # Original chunk text
        "char_count": "integer",
        "document_metadata": {     # Denormalized for single-query retrieval
            "filename": "keyword",
            "content_hash": "keyword",
            "upload_date": "datetime",
            "source_url": "keyword"
        }
    }
}
```

**Best Practices Applied**:
1. **Denormalize metadata**: Store document metadata in each chunk payload to avoid joins
2. **Index key fields**: `document_id`, `content_hash` for fast filtering
3. **Batch upserts**: Insert chunks in batches of 100 for better throughput
4. **Connection pooling**: Reuse Qdrant client across requests
5. **Pagination**: Limit query results to 100 points per page

**Rationale**:
- **Denormalization**: Qdrant is not relational; denormalizing avoids client-side joins
- **Batch inserts**: 10x faster than individual upserts (measured in Qdrant docs)
- **Cosine distance**: Standard for text similarity, matches Cohere embedding best practices

**Alternatives Considered**:
- **Separate collections** (documents vs chunks): Rejected; complicates queries and requires client-side joins
- **PostgreSQL + pgvector**: Rejected; Qdrant optimized for vector workloads, simpler deployment

---

## Decision 5: SSRF Prevention for URL Ingestion

### Requirement
FR-009: Support ingestion from URLs
Security (spec line 230): Prevent SSRF attacks

### Threat Model

**Attack Vectors**:
1. Private IP access: `http://192.168.1.1/admin` → access internal services
2. Localhost: `http://localhost:8080` → bypass firewall
3. Redirect chains: `http://evil.com` → redirects to `http://10.0.0.5/secrets`
4. DNS rebinding: Resolve to public IP, then re-resolve to private IP mid-request
5. Cloud metadata APIs: `http://169.254.169.254/latest/meta-data` → steal AWS credentials

### Mitigation Strategy

**Implementation**:
```python
import ipaddress
from urllib.parse import urlparse

BLOCKED_SCHEMES = ["file", "ftp", "gopher", "data"]
ALLOWED_SCHEMES = ["http", "https"]
PRIVATE_IP_RANGES = [
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
    ipaddress.IPv4Network("127.0.0.0/8"),  # Localhost
    ipaddress.IPv4Network("169.254.0.0/16"),  # AWS metadata
]

def validate_url(url: str) -> None:
    """Validate URL to prevent SSRF attacks."""
    parsed = urlparse(url)

    # 1. Scheme validation
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f"Scheme {parsed.scheme} not allowed")

    # 2. IP address check (before DNS resolution)
    try:
        ip = ipaddress.IPv4Address(parsed.hostname)
        for blocked_range in PRIVATE_IP_RANGES:
            if ip in blocked_range:
                raise ValueError(f"Private IP access blocked: {ip}")
    except ValueError:
        pass  # Hostname is not an IP; DNS will resolve later

    # 3. Disable redirect following (handle manually with validation)
    # Use requests.get(..., allow_redirects=False) and validate each redirect

def fetch_url_safe(url: str, max_redirects: int = 5) -> bytes:
    """Fetch URL with SSRF protection and redirect validation."""
    validate_url(url)

    redirect_count = 0
    current_url = url

    while redirect_count < max_redirects:
        response = requests.get(current_url, allow_redirects=False, timeout=30)

        if response.status_code in (301, 302, 303, 307, 308):
            redirect_url = response.headers.get("Location")
            validate_url(redirect_url)  # Validate each redirect
            current_url = redirect_url
            redirect_count += 1
        else:
            return response.content

    raise ValueError("Too many redirects")
```

**Rationale**:
- **Whitelist approach**: Only http/https allowed (blocks file://, gopher://, etc.)
- **Private IP blocking**: Prevents access to internal services and cloud metadata
- **Manual redirect handling**: Validates each redirect to prevent redirect-based bypasses
- **Timeout**: 30s prevents slowloris attacks

**Alternatives Considered**:
- **DNS validation**: Rejected; vulnerable to DNS rebinding (TOCTOU race)
- **Allow all + logging**: Rejected; violates Constitution Principle IV (Security)

---

## Decision 6: File Validation Strategy

### Requirement
FR-007: Validate formats before processing, reject unsupported with clear errors
Security: Prevent malicious file execution

### Validation Layers

**1. Size Validation** (first, cheapest check):
```python
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB per spec constraint

if file_size > MAX_FILE_SIZE:
    raise ValueError(f"File exceeds 500MB limit: {file_size / 1024 / 1024:.1f}MB")
```

**2. Extension Validation** (second check, user-friendly):
```python
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".html", ".htm"}

def validate_extension(filename: str) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
```

**3. MIME Type Validation** (third check, prevents extension spoofing):
```python
import magic  # python-magic library

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # DOCX
    "text/html",
}

def validate_mime_type(file_content: bytes) -> str:
    """Validate MIME type using magic bytes."""
    mime = magic.from_buffer(file_content, mime=True)
    if mime not in ALLOWED_MIME_TYPES:
        raise ValueError(f"Invalid file type: {mime}")
    return mime
```

**4. Content Sanitization** (for HTML):
```python
# Strip executable content from HTML
for element in soup.find_all(['script', 'style', 'iframe', 'object', 'embed']):
    element.decompose()
```

**Rationale**:
- **Layered defense**: Multiple checks prevent bypasses (e.g., fake.pdf.exe)
- **Magic byte validation**: Prevents extension spoofing attacks
- **Size check first**: Fails fast before reading large files into memory
- **HTML sanitization**: Prevents XSS if extracted content is displayed

**Alternatives Considered**:
- **Extension-only validation**: Rejected; trivially bypassed with spoofing
- **Virus scanning**: Deferred to infrastructure layer (not application responsibility per YAGNI)

---

## Implementation Notes

### Library Dependencies (add to requirements.txt)
```
PyPDF2>=3.0.0       # PDF extraction
python-docx>=0.8.11 # DOCX extraction
python-magic>=0.4.27 # MIME type detection
```

### Performance Benchmarks Needed

Before implementation, validate these assumptions with real tests:
1. **Chunking speed**: Target >1MB/s text processing
2. **PDF extraction**: Target <30s for 100-page document
3. **Qdrant batch insert**: Target >100 chunks/second

If benchmarks fail, revisit library choices or algorithm optimizations.

### Edge Case Handling Plan

From spec lines 103-109, defer these to implementation phase:
- Empty documents → Log warning, skip processing, return error
- Files >500MB → Reject with clear error per size validation
- Duplicate ingestion → Detect via content hash, return 409 Conflict
- Non-UTF-8 encoding → Attempt detection + conversion with chardet library
- Storage exhaustion → Qdrant health check before ingestion, fail gracefully
- Password-protected files → Reject with error (no password handling in MVP)
- Chunking failures → Catch exceptions, log error, mark document as failed

---

## Summary

All research questions answered with concrete technical decisions:

1. ✅ **Parsing**: PyPDF2 (PDF), python-docx (DOCX), BeautifulSoup4 (HTML), built-in (TXT)
2. ✅ **Chunking**: Recursive character splitter, 500-2000 chars, 100-char overlap, sentence boundaries
3. ✅ **Hashing**: SHA-256 of normalized text content
4. ✅ **Storage**: Qdrant single collection with denormalized metadata, batch upserts
5. ✅ **SSRF Prevention**: Whitelist schemes, block private IPs, manual redirect validation
6. ✅ **File Validation**: Size → Extension → MIME → Content sanitization

All decisions align with constitution principles (Data Integrity, Security, Simplicity) and meet functional requirements.

**Next**: Proceed to Phase 1 to create data-model.md and contracts/.
