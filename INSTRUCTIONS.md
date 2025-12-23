# RAG-Enabled Agent Service

This project implements a RAG (Retrieval-Augmented Generation) agent service that allows users to ask questions about the Physical AI & Humanoid Robotics textbook and receive grounded answers based on the embedded content.

## Features

- Document ingestion pipeline that loads content from sitemaps or URLs
- Content cleaning and chunking for processing
- Vector embedding using Cohere and storage in Qdrant
- FastAPI endpoints for question answering and retrieval
- OpenAI agent integration with grounding instructions
- Health and metadata endpoints for monitoring

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`
- Environment variables configured in `.env` file

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:
   ```
   QDRANT_URL=your_qdrant_url
   QDRANT_API_KEY=your_qdrant_api_key
   COHERE_API_KEY=your_cohere_api_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

### Run the document ingestion pipeline:
```bash
python main.py
```

### Run the retrieval validation:
```bash
python main.py --validate-retrieval
```

### Start the FastAPI server:
```bash
python main.py --start-server
```

The server will start at `http://0.0.0.0:8000` by default. You can specify a different host and port:
```bash
python main.py --start-server --host 127.0.0.1 --port 8080
```

## API Endpoints

### `/ask` (POST)
Ask a question and get a grounded answer.

Request body:
```json
{
  "question": "Your question here",
  "selected_text": "Optional text to use instead of retrieval",
  "top_k": 5,
  "temperature": 0.2
}
```

Response:
```json
{
  "answer": "The answer to your question",
  "citations": ["List of source citations"],
  "reasoning": "Explanation of how the answer was derived",
  "metadata": "Additional metadata about the request"
}
```

### `/retrieve` (POST)
Direct retrieval of document chunks.

Request body:
```json
{
  "query": "Your search query",
  "top_k": 5
}
```

Response:
```json
{
  "query": "Your search query",
  "results": ["List of retrieved chunks"],
  "count": "Number of results"
}
```

### `/health` (GET)
Get service health status.

Response:
```json
{
  "status": "healthy|degraded|unhealthy",
  "model": "gpt-4o",
  "collection_name": "documents",
  "qdrant_connected": true
}
```

### `/metadata` (GET)
Get service metadata.

Response:
```json
{
  "embedding_model": "embed-english-v3.0",
  "vector_size": 1024,
  "chunk_count": 1234,
  "total_chunks": 1234
}
```

## Architecture

The system consists of:

1. **Document Ingestion Pipeline**: Loads, cleans, chunks, and embeds documents
2. **Vector Storage**: Stores embeddings in Qdrant for efficient retrieval
3. **Retrieval Component**: Finds relevant document chunks based on user queries
4. **OpenAI Agent**: Generates grounded answers based on retrieved content
5. **FastAPI Service**: Exposes endpoints for user interaction

## Environment Variables

- `QDRANT_URL`: URL for Qdrant vector database
- `QDRANT_API_KEY`: API key for Qdrant (if required)
- `COHERE_API_KEY`: API key for Cohere embedding service
- `OPENAI_API_KEY`: API key for OpenAI service
- `SITEMAP_URL`: URL to sitemap.xml for document loading (optional)
- `BOOK_URLS`: Comma-separated list of URLs to load (optional)