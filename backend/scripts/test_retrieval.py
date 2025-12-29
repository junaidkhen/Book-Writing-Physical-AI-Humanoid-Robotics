#!/usr/bin/env python3
"""
Test retrieval quality with various queries
"""
import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import cohere

# Load environment
backend_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path=env_path)

def test_query(query: str, client: QdrantClient, cohere_client, collection_name: str, top_k: int = 5):
    """Test a single query and show results"""
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}")

    # Generate query embedding
    response = cohere_client.embed(
        texts=[query],
        model="embed-english-v3.0",
        input_type="search_query"
    )
    query_embedding = response.embeddings[0]

    # Search WITHOUT score threshold
    results_no_threshold = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k
    )

    # Search WITH score threshold
    results_with_threshold = client.search(
        collection_name=collection_name,
        query_vector=query_embedding,
        limit=top_k,
        score_threshold=0.5  # Common threshold
    )

    print(f"\n📊 Results WITHOUT score threshold (top {top_k}):")
    print("-" * 80)
    for idx, result in enumerate(results_no_threshold, 1):
        payload = result.payload
        score = result.score

        # Get content
        content = payload.get('text_content') or payload.get('content', '')
        content_preview = content[:150] + "..." if len(content) > 150 else content

        # Get source info
        doc_meta = payload.get('document_metadata', {})
        source_url = doc_meta.get('source_url', 'N/A')

        print(f"\n{idx}. Score: {score:.4f}")
        print(f"   Source: {source_url}")
        print(f"   Content: {content_preview}")

    print(f"\n\n📊 Results WITH score threshold ≥ 0.5 (top {top_k}):")
    print("-" * 80)
    if not results_with_threshold:
        print("   ⚠️  NO RESULTS! All scores below 0.5 threshold")
    else:
        for idx, result in enumerate(results_with_threshold, 1):
            payload = result.payload
            score = result.score

            content = payload.get('text_content') or payload.get('content', '')
            content_preview = content[:150] + "..." if len(content) > 150 else content

            doc_meta = payload.get('document_metadata', {})
            source_url = doc_meta.get('source_url', 'N/A')

            print(f"\n{idx}. Score: {score:.4f}")
            print(f"   Source: {source_url}")
            print(f"   Content: {content_preview}")

def main():
    # Get credentials from environment
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "documents")

    if not all([qdrant_url, qdrant_api_key, cohere_api_key]):
        print("❌ Error: Missing environment variables")
        return 1

    print(f"🔍 Testing retrieval on collection: '{collection_name}'")
    print(f"🔗 Qdrant URL: {qdrant_url}")

    # Initialize clients
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    cohere_client = cohere.Client(cohere_api_key)

    # Test queries - mix of specific and general
    test_queries = [
        "What is physical AI?",
        "How do humanoid robots maintain balance?",
        "Explain computer vision in robotics",
        "What are degrees of freedom in robotics?",
        "Tell me about reinforcement learning for robots",
        "What is the history of robotics?",
        "How do robots use sensors for perception?",
        "What is motion planning?"
    ]

    for query in test_queries:
        test_query(query, client, cohere_client, collection_name, top_k=5)

    return 0

if __name__ == "__main__":
    sys.exit(main())
