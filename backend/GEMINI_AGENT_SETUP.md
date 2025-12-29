# Gemini 2.5 Flash RAG Agent Setup Guide

## Overview

This RAG chatbot agent uses **Gemini 2.5 Flash** via Google's OpenAI-compatible API endpoint to provide documentation-focused responses based on context retrieved from Qdrant vector database.

## Architecture

```
User Query → FastAPI Endpoint → RAG Agent
                                    ↓
                    1. Query → Cohere Embeddings
                    2. Vector Search → Qdrant Database
                    3. Context + Query → Gemini 2.5 Flash
                    4. Response → User
```

## Features

- **Free Tier Model**: Uses Gemini 2.5 Flash (free API tier)
- **Async Architecture**: AsyncOpenAI client with FastAPI
- **Vector Search**: Cohere embeddings + Qdrant vector database
- **Context-Grounded**: Responses strictly based on retrieved documentation
- **Error Handling**: Comprehensive API error handling with fallback messages
- **Token Limits**: Max 500 tokens per response (configurable)

## Prerequisites

1. **Gemini API Key** (free tier)
   - Get yours at: https://aistudio.google.com/app/apikey

2. **Cohere API Key** (for embeddings)
   - Get yours at: https://dashboard.cohere.com/api-keys

3. **Qdrant** (vector database)
   - Local: `docker run -p 6333:6333 qdrant/qdrant`
   - Or use Qdrant Cloud

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Required: Cohere API Key (for embeddings)
COHERE_API_KEY=your_cohere_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=documents

# Optional: Model Configuration
GEMINI_MODEL=gemini-2.5-flash
TEMPERATURE=0.1
MAX_TOKENS=500
TOP_K=5
```

### 3. Verify Qdrant Collection

Ensure your Qdrant collection is populated with document embeddings:

```bash
# Check collection exists
curl http://localhost:6333/collections/documents
```

## Usage

### Starting the Server

```bash
cd backend
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

#### 1. Ask Endpoint (Non-Streaming)

```bash
POST http://localhost:8000/api/v1/ask
Content-Type: application/json

{
  "query": "What is physical AI?",
  "top_k": 5,
  "temperature": 0.1
}
```

**Response:**
```json
{
  "answer": "Physical AI refers to...",
  "citations": [
    {
      "chunk_id": "12345",
      "chapter": "Introduction",
      "section": "Overview",
      "page": 1,
      "score": 0.95
    }
  ],
  "reasoning": [
    "Query interpretation: Answering 'What is physical AI?...'",
    "Retrieval results: Found 5 relevant chunks from the textbook",
    "Synthesis logic: Generated answer using Gemini 2.5 Flash based on retrieved context"
  ],
  "metadata": {
    "token_usage": {
      "input_tokens": 450,
      "output_tokens": 120,
      "total_tokens": 570
    },
    "retrieval_time": 150.5,
    "agent_time": 890.2,
    "total_time": 1040.7,
    "chunks_retrieved": 5
  }
}
```

#### 2. Chat Endpoint (Streaming)

```bash
POST http://localhost:8000/api/v1/chat
Content-Type: application/json

{
  "query": "Explain humanoid robotics",
  "stream": true
}
```

**Server-Sent Events (SSE) Response:**
```
data: {"type": "content", "data": {"text": "Humanoid robotics..."}}
data: {"type": "citation", "data": {...}}
data: {"type": "done", "data": {}}
```

## Key Implementation Details

### RAG Agent (backend/src/agents/rag_agent.py)

```python
from openai import AsyncOpenAI

# Initialize with Gemini endpoint
self.client = AsyncOpenAI(
    api_key=settings.gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# Async query method
async def generate_answer(self, query: str, top_k: int = 5):
    # 1. Retrieve chunks from Qdrant
    retrieved_chunks, _ = await retrieve_chunks(query, top_k)

    # 2. Format context
    context = format_context(retrieved_chunks)

    # 3. Call Gemini API
    response = await self.client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[...],
        temperature=0.1,
        max_tokens=500
    )

    return response
```

### Configuration (backend/src/config/settings.py)

```python
class Settings(BaseSettings):
    # Gemini Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-2.5-flash"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # Application Settings
    temperature: float = 0.1
    max_tokens: int = 500
    top_k: int = 5
```

## Error Handling

The agent includes comprehensive error handling for:

1. **Quota Exceeded**: "Gemini API quota exceeded or rate limit reached"
2. **Authentication**: "Invalid Gemini API key"
3. **Model Not Found**: "Model gemini-2.5-flash not available"
4. **No Results**: Fallback message when no relevant documents found

## Response Constraints

Per requirements, responses are:
- **Plain text** format (no markdown unless requested)
- **Maximum 500 tokens**
- **Documentation-focused** and grounded in retrieved context
- **Concise** and directly answerable

## Testing

### Manual Test

```bash
curl -X POST http://localhost:8000/api/v1/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key components of a humanoid robot?",
    "top_k": 5,
    "temperature": 0.1
  }'
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health
```

## Troubleshooting

### Issue: "Invalid Gemini API key"
**Solution**: Verify your `GEMINI_API_KEY` in `.env` is correct

### Issue: "No relevant documents found"
**Solution**:
1. Check Qdrant is running: `curl http://localhost:6333/collections`
2. Verify collection has documents: `curl http://localhost:6333/collections/documents`
3. Re-run document ingestion if needed

### Issue: "Cohere API error"
**Solution**: Verify `COHERE_API_KEY` is set correctly in `.env`

## Model Information

- **Model**: gemini-2.5-flash
- **API Tier**: Free (with rate limits)
- **Endpoint**: https://generativelanguage.googleapis.com/v1beta/openai/
- **Compatibility**: OpenAI-compatible API
- **Documentation**: https://ai.google.dev/gemini-api/docs

## Files Modified

- `backend/src/agents/rag_agent.py` - Refactored to use AsyncOpenAI with Gemini
- `backend/src/config/settings.py` - Added Gemini configuration
- `backend/.env.example` - Updated with Gemini API key template

## Performance Notes

- **Average Response Time**: 1-2 seconds (depends on network and API latency)
- **Retrieval Time**: ~150-300ms (Qdrant vector search)
- **Agent Time**: ~800-1200ms (Gemini API call)
- **Token Usage**: Typically 300-500 tokens per query (context + response)

## Next Steps

1. Set up your Gemini API key in `.env`
2. Ensure Qdrant is running with populated collection
3. Start the FastAPI server
4. Test with sample queries
5. Integrate with Docusaurus frontend chatbot widget

## Support

For issues or questions:
- Gemini API Docs: https://ai.google.dev/gemini-api/docs
- OpenAI Python SDK: https://github.com/openai/openai-python
- Qdrant Docs: https://qdrant.tech/documentation/
