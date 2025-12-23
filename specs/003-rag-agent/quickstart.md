# Quickstart Guide: RAG-Enabled Agent Service

## Overview
This guide provides a quick setup and usage guide for the RAG-Enabled Agent Service (003-rag-agent). This service uses OpenAI Agents SDK and FastAPI to retrieve knowledge from Qdrant and produce grounded, citation-based answers from embedded book content.

## Prerequisites
- Python 3.11+
- OpenAI API key
- Qdrant instance with pre-embedded book content (from Spec-1)
- Git

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
git checkout 003-rag-agent
```

### 2. Set up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip
```

### 3. Install Dependencies
```bash
pip install openai fastapi uvicorn python-dotenv qdrant-client pydantic
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here  # if authentication required
QDRANT_COLLECTION_NAME=book_embeddings  # or your collection name from Spec-1
OPENAI_MODEL=gpt-4o  # or gpt-4-turbo
TEMPERATURE=0.1
TOP_K_DEFAULT=5
```

## Running the Service

### 1. Start the Service
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000`

### 2. Verify Installation
Check the API documentation at `http://localhost:8000/docs`

## API Usage Examples

### 1. Ask a Question
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key components of a humanoid robot?",
    "top_k": 5,
    "temperature": 0.1
  }'
```

### 2. Retrieve Raw Chunks
```bash
curl -X POST http://localhost:8000/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sensor fusion methods",
    "top_k": 3
  }'
```

### 3. Check Health
```bash
curl http://localhost:8000/health
```

### 4. Get Metadata
```bash
curl http://localhost:8000/metadata
```

## Key Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `QDRANT_URL`: URL to your Qdrant instance (required)
- `QDRANT_API_KEY`: Qdrant API key if authentication is enabled
- `QDRANT_COLLECTION_NAME`: Name of the collection with book embeddings
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4o)
- `TEMPERATURE`: Response randomness (0.0-0.2, default: 0.1)
- `TOP_K_DEFAULT`: Default number of chunks to retrieve (default: 5)

### Runtime Parameters
- `top_k`: Number of chunks to retrieve (1-20)
- `temperature`: Response randomness for specific requests (0.0-0.2)

## Development

### Project Structure
```
specs/003-rag-agent/
├── main.py              # Main application entry point
├── config.py            # Configuration management
├── retrieval.py         # Qdrant retrieval logic
├── agent.py             # OpenAI agent logic
├── models.py            # Pydantic models
├── api/
│   ├── __init__.py
│   └── endpoints.py     # API endpoints
└── tests/
    ├── __init__.py
    ├── test_api.py      # API tests
    └── test_retrieval.py # Retrieval tests
```

### Testing
Run the test suite:
```bash
python -m pytest tests/ -v
```

### Adding New Features
1. Update the spec if requirements change
2. Update data models in `models.py`
3. Implement new functionality following the existing patterns
4. Add tests for new functionality
5. Update documentation as needed

## Troubleshooting

### Common Issues

#### Qdrant Connection Issues
- Verify `QDRANT_URL` is correct
- Check that the Qdrant instance is running
- Ensure the collection name matches your Spec-1 implementation

#### OpenAI API Issues
- Verify `OPENAI_API_KEY` is valid and has sufficient quota
- Check that the specified model is available in your region

#### Query Performance
- If responses are slow, consider reducing `top_k` value
- Check Qdrant indexing and ensure embeddings are properly stored

### Health Check Response Meanings
- `healthy`: All systems operational
- `degraded`: Service operational but one or more dependencies have issues
- `unhealthy`: Service cannot function properly

## Next Steps
1. Review the full API documentation at `/docs`
2. Check the data models in `data-model.md`
3. Look at the implementation plan in `plan.md`
4. Run the end-to-end tests to verify functionality