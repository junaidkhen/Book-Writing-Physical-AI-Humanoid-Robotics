# Quickstart Guide: Document Ingestion Core System

**Feature**: 002-document-ingestion-core
**Date**: 2025-12-17
**Audience**: Developers integrating with or extending the document ingestion pipeline

## Overview

This guide walks you through setting up, running, and testing the document ingestion service in under 15 minutes.

**What you'll build**:
- Document ingestion pipeline (PDF, TXT, DOCX, HTML)
- Text extraction and chunking
- Vector embeddings with Cohere
- Storage in Qdrant vector database
- FastAPI REST endpoints for ingestion and queries

---

## Prerequisites

### Required

- **Python**: 3.11 or higher
- **Qdrant**: Running instance (Docker or cloud)
- **API Keys**: Cohere API key for embeddings

### Optional

- **Docker**: For running Qdrant locally
- **Git**: For cloning the repository

---

## Setup (5 minutes)

### Step 1: Install Dependencies

```bash
# Navigate to project root
cd /path/to/Book-Wr-Claude

# Create virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

**requirements.txt** should contain:
```
requests>=2.28.0
beautifulsoup4>=4.11.0
qdrant-client>=1.6.0
cohere>=4.0.0
python-dotenv>=0.19.0
fastapi>=0.104.0
uvicorn>=0.24.0
openai>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.6
pytest>=7.4.0
PyPDF2>=3.0.0        # For PDF extraction
python-docx>=0.8.11  # For DOCX extraction
python-magic>=0.4.27 # For MIME type detection
```

### Step 2: Start Qdrant (Docker)

```bash
# Pull and run Qdrant
docker run -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage:z \
  qdrant/qdrant:latest
```

**Qdrant will be available at**: `http://localhost:6333`

**Verify Qdrant is running**:
```bash
curl http://localhost:6333/health
# Expected: {"status":"ok","version":"1.x.x"}
```

### Step 3: Configure Environment Variables

Create `.env` file in project root:

```bash
# Copy example
cp .env.example .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

**.env contents**:
```bash
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=  # Leave empty for local instance

# Cohere API Key (get from https://dashboard.cohere.com/api-keys)
COHERE_API_KEY=your_cohere_api_key_here

# OpenAI API Key (optional - for RAG agent)
OPENAI_API_KEY=your_openai_api_key_here

# Sitemap URL (for automatic URL discovery)
SITEMAP_URL=https://book-writing-physical-ai-humanoid-r.vercel.app/sitemap.xml

# Or manual URL list (comma-separated)
BOOK_URLS=https://example.com/page1,https://example.com/page2

# Logging
LOG_LEVEL=INFO
```

**Important**: Add `.env` to `.gitignore` to prevent committing secrets!

---

## Quick Test (3 minutes)

### Test 1: Verify Imports

```bash
python3 -c "
import requests
import qdrant_client
import cohere
from dotenv import load_dotenv
print('✅ All imports successful')
"
```

### Test 2: Test Qdrant Connection

```python
# test_qdrant.py
from qdrant_client import QdrantClient
import os
from dotenv import load_dotenv

load_dotenv()

client = QdrantClient(url=os.getenv("QDRANT_URL"))
collections = client.get_collections()
print(f"✅ Qdrant connected. Collections: {collections}")
```

```bash
python test_qdrant.py
```

### Test 3: Test Cohere API

```python
# test_cohere.py
import cohere
import os
from dotenv import load_dotenv

load_dotenv()

co = cohere.Client(os.getenv("COHERE_API_KEY"))
response = co.embed(
    texts=["Hello world"],
    model="embed-english-v3.0"
)
print(f"✅ Cohere API working. Embedding dimension: {len(response.embeddings[0])}")
```

```bash
python test_cohere.py
```

---

## Running the Ingestion Pipeline (2 minutes)

### Option A: Using Existing main.py (Prototype)

```bash
# Run the ingestion pipeline
python3 main.py
```

**Expected Output**:
```
2025-12-17 11:00:00 - INFO - Loaded 25 unique URLs
2025-12-17 11:00:01 - INFO - Fetching content from https://example.com/page1
2025-12-17 11:00:02 - INFO - Extracted 1234 characters
2025-12-17 11:00:03 - INFO - Generated 3 chunks
2025-12-17 11:00:04 - INFO - Embedded 3 chunks
2025-12-17 11:00:05 - INFO - Stored 3 vectors in Qdrant
...
2025-12-17 11:05:00 - INFO - Pipeline complete: 25 documents, 642 chunks
```

### Option B: Start FastAPI Server

```bash
# Start FastAPI development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access Interactive API Docs**: http://localhost:8000/docs

---

## Example Usage (5 minutes)

### Example 1: Ingest Single File

```bash
# Upload a PDF file
curl -X POST http://localhost:8000/api/v1/ingest/file \
  -F "file=@robotics-chapter-1.pdf"
```

**Response**:
```json
{
  "job_id": "b2c3d4e5-6789-01ab-cdef-2345678901bc",
  "document_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "status": "pending",
  "message": "Document accepted for processing"
}
```

### Example 2: Ingest from URL

```bash
curl -X POST http://localhost:8000/api/v1/ingest/url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://book-writing-physical-ai-humanoid-r.vercel.app/docs/intro"
  }'
```

### Example 3: Check Ingestion Status

```bash
# Check job status
curl http://localhost:8000/api/v1/ingest/job/b2c3d4e5-6789-01ab-cdef-2345678901bc
```

**Response**:
```json
{
  "job_id": "b2c3d4e5-6789-01ab-cdef-2345678901bc",
  "status": "completed",
  "total_documents": 1,
  "documents_processed": 1,
  "documents_failed": 0,
  "started_at": "2025-12-17T11:00:00Z",
  "completed_at": "2025-12-17T11:00:15Z"
}
```

### Example 4: Query Qdrant Directly

```python
# query_qdrant.py
from qdrant_client import QdrantClient
import cohere
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize clients
qdrant = QdrantClient(url=os.getenv("QDRANT_URL"))
co = cohere.Client(os.getenv("COHERE_API_KEY"))

# Embed query
query = "What is physical AI?"
query_embedding = co.embed(
    texts=[query],
    model="embed-english-v3.0"
).embeddings[0]

# Search Qdrant
results = qdrant.search(
    collection_name="documents",
    query_vector=query_embedding,
    limit=5
)

# Print top results
for i, result in enumerate(results, 1):
    print(f"\n--- Result {i} (score: {result.score:.3f}) ---")
    print(result.payload["text_content"][:200])
    print(f"Source: {result.payload['document_metadata']['filename']}")
```

```bash
python query_qdrant.py
```

---

## Testing

### Run Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_chunking.py -v

# Run with coverage
pytest tests/ --cov=backend/src --cov-report=html
```

### Run Contract Tests

```bash
# Test API endpoints match OpenAPI spec
pytest tests/contract/test_ingestion_api.py -v
```

### Manual Testing

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Metrics
curl http://localhost:8000/api/v1/metrics

# List documents
curl "http://localhost:8000/api/v1/documents?limit=10&status=completed"
```

---

## Common Issues & Solutions

### Issue 1: Qdrant Connection Failed

**Error**: `QdrantConnectionError: Could not connect to Qdrant`

**Solution**:
1. Check Qdrant is running: `curl http://localhost:6333/health`
2. Verify `QDRANT_URL` in `.env` matches Qdrant instance
3. Restart Qdrant container if needed

### Issue 2: Cohere API Authentication Failed

**Error**: `cohere.CohereAPIError: invalid api key`

**Solution**:
1. Verify API key in `.env`: `echo $COHERE_API_KEY`
2. Get new key from https://dashboard.cohere.com/api-keys
3. Ensure no spaces/quotes in `.env` value

### Issue 3: Import Errors

**Error**: `ModuleNotFoundError: No module named 'cohere'`

**Solution**:
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 4: File Too Large

**Error**: `413 Payload Too Large`

**Solution**:
- Check file size: `ls -lh file.pdf`
- Max size is 500MB per spec
- Split large PDFs or compress

### Issue 5: Unsupported File Type

**Error**: `400 Bad Request: Unsupported file type: .exe`

**Solution**:
- Only PDF, TXT, DOCX, HTML supported
- Check file extension matches actual content
- Convert to supported format

---

## Project Structure

```
Book-Wr-Claude/
├── backend/                 # Backend ingestion service (future)
│   ├── src/
│   │   ├── models/         # Document, Chunk, IngestionJob
│   │   ├── services/       # Ingestion, extraction, chunking
│   │   ├── api/            # FastAPI endpoints
│   │   └── main.py         # App initialization
│   └── tests/
│       ├── contract/       # API contract tests
│       ├── integration/    # External service tests
│       └── unit/           # Business logic tests
├── docs/                    # Docusaurus frontend
├── specs/                   # Feature specifications
│   └── 002-document-ingestion-core/
│       ├── spec.md
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md   # This file
│       └── contracts/
├── main.py                  # Current prototype (root level)
├── requirements.txt
├── .env                     # Environment variables (gitignored)
└── .env.example             # Template for .env
```

---

## Next Steps

1. ✅ **Setup complete**: Environment configured, dependencies installed
2. ⏭️ **Explore API**: Visit http://localhost:8000/docs for interactive docs
3. ⏭️ **Ingest documents**: Upload your own PDFs/documents
4. ⏭️ **Query knowledge base**: Test retrieval with `query_qdrant.py`
5. ⏭️ **Extend**: Add new file formats, improve chunking, optimize embeddings

---

## Development Workflow

### 1. Create New Feature Branch

```bash
git checkout -b feature/improve-chunking
```

### 2. Make Changes with TDD

```bash
# 1. Write failing test
# tests/unit/test_chunking.py

def test_chunking_preserves_sentence_boundaries():
    text = "This is sentence one. This is sentence two."
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    # Assert chunks don't break mid-sentence

# 2. Run test (should fail)
pytest tests/unit/test_chunking.py::test_chunking_preserves_sentence_boundaries

# 3. Implement feature
# backend/src/services/chunking.py

# 4. Run test (should pass)
pytest tests/unit/test_chunking.py::test_chunking_preserves_sentence_boundaries

# 5. Refactor and repeat
```

### 3. Run Full Test Suite

```bash
pytest tests/ --cov=backend/src --cov-report=term-missing
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: improve sentence boundary detection in chunking

- Add recursive character splitting with sentence tokenization
- Preserve semantic boundaries per FR-003
- Add test coverage for edge cases

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Resources

- **Spec**: [spec.md](spec.md) - Feature requirements and user stories
- **Plan**: [plan.md](plan.md) - Technical architecture and decisions
- **Data Model**: [data-model.md](data-model.md) - Entity definitions and schemas
- **API Contracts**: [contracts/](contracts/) - OpenAPI specifications
- **Research**: [research.md](research.md) - Library evaluations and technical decisions
- **Constitution**: [.specify/memory/constitution.md](../../.specify/memory/constitution.md) - Project principles

---

## Support

**Questions?** Check these resources:

1. **FastAPI Docs**: https://fastapi.tiangolo.com/
2. **Qdrant Docs**: https://qdrant.tech/documentation/
3. **Cohere Docs**: https://docs.cohere.com/
4. **PyPDF2 Docs**: https://pypdf2.readthedocs.io/
5. **BeautifulSoup Docs**: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

**Issues?** File a bug report with:
- Steps to reproduce
- Error message (full traceback)
- Environment (OS, Python version, dependency versions)
- Expected vs actual behavior

---

**🎉 Congratulations!** You've set up the document ingestion pipeline. Happy coding!
