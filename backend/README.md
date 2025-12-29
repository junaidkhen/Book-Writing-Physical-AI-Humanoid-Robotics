# RAG-Enabled Agent Service

This service implements a Retrieval-Augmented Generation (RAG) agent that answers questions about the Physical AI & Humanoid Robotics textbook using OpenAI and Qdrant vector database.

## Features

- **Question Answering**: Ask questions about the textbook content and receive grounded answers
- **Direct Retrieval**: Retrieve raw book chunks relevant to queries without agent synthesis
- **Citations**: Answers include citations to specific book sections
- **Reasoning**: Step-by-step reasoning for how answers were generated
- **Health Checks**: Monitor service and dependency status
- **Metrics**: Performance and usage statistics

## Architecture

The service follows a microservice architecture with:

- **FastAPI**: Web framework for building the API
- **OpenAI API**: Language model for generating answers
- **Qdrant**: Vector database for semantic search
- **Cohere**: Alternative embedding service (optional)

## API Endpoints

### `/api/v1/ask` (POST)
Process a query and return a grounded answer with citations.

Request body:
```json
{
  "query": "Your question here",
  "top_k": 5,
  "temperature": 0.1
}
```

### `/api/v1/retrieve` (POST)
Retrieve raw book chunks relevant to a query.

Request body:
```json
{
  "query": "Your search query",
  "top_k": 5
}
```

### `/api/v1/health` (GET)
Check service and dependency health.

### `/api/v1/metadata` (GET)
Get service configuration and performance metrics.

## Environment Variables

Create a `.env` file with the following variables:

```bash
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=documents

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Cohere Configuration (if needed)
COHERE_API_KEY=your_cohere_api_key_here

# Application Configuration
TEMPERATURE=0.1
TOP_K=5
MAX_TOKENS=4000
DEBUG=false
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Service

```bash
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

Or run directly:
```bash
cd backend
python -m src.main
```

## Testing

Run the test suite:
```bash
cd backend
pytest
```

## Docker Deployment

To build and run with Docker:

```bash
# Build the image
docker build -t rag-agent-service .

# Run the container
docker run -p 8000:8000 --env-file .env rag-agent-service
```

## Configuration

- **Temperature**: Controls randomness (0.0-0.2, lower for more deterministic responses)
- **Top-K**: Number of chunks to retrieve (1-20)
- **Max Tokens**: Maximum tokens for responses

## Security

- API keys are loaded from environment variables
- Input validation on all endpoints
- Structured logging with sensitive data filtering
- CORS configured for frontend integration

## Monitoring

The service provides:
- Health checks at `/api/v1/health`
- Performance metrics at `/api/v1/metadata`
- Structured JSON logs
- Error tracking and reporting

## Dependencies

- Python 3.11+
- FastAPI
- OpenAI API
- Qdrant Vector Database
- Cohere (optional)
