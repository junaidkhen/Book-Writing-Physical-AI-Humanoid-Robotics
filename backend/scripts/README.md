# Sitemap Ingestion Script

This script fetches URLs from a sitemap.xml file and ingests the content into Qdrant vector database using Cohere embeddings.

## Purpose

The sitemap_ingestion.py script is designed to:
- Fetch all URLs from a provided sitemap.xml file
- Extract content from each URL
- Process the content using the existing ingestion pipeline
- Store the content in Qdrant vector database with Cohere embeddings
- Make the content available for the RAG agent to use

## Prerequisites

Before running the script, ensure that:
1. You have the required environment variables set in your `.env` file:
   - `QDRANT_URL`: Your Qdrant instance URL
   - `QDRANT_API_KEY`: Your Qdrant API key
   - `QDRANT_COLLECTION_NAME`: Collection name (default: documents)
   - `COHERE_API_KEY`: Your Cohere API key
   - `SITEMAP_URL`: The URL to your sitemap.xml file

2. The backend dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script using Python:

```bash
cd backend
python scripts/sitemap_ingestion.py
```

## Process

The script will:
1. Fetch the sitemap.xml from the configured URL
2. Extract all URLs from the sitemap
3. For each URL:
   - Fetch the content
   - Extract text from the page
   - Create temporary files
   - Ingest the content using the standard ingestion pipeline
   - Store embeddings in Qdrant
4. Report the results (successful/failed ingests)

## Configuration

The script reads configuration from environment variables in the `.env` file:
- `SITEMAP_URL`: URL to the sitemap.xml file to process
- Other variables are used for connecting to Qdrant and Cohere services

## Logging

The script uses the same logging configuration as the rest of the application, with structured JSON logs.

## Rate Limiting

The script includes a 1-second delay between requests to be respectful to the source server.