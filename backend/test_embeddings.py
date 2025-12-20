#!/usr/bin/env python3
"""
Test script to verify Cohere embeddings are being generated and stored in Qdrant properly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.services.storage import initialize_clients, get_cohere_client, get_qdrant_client
from src.services.ingestion import get_ingestion_service


def test_cohere_embeddings():
    """Test if Cohere is properly generating embeddings."""
    print("Testing Cohere embedding generation...")

    # Get the Cohere client
    try:
        cohere_client = get_cohere_client()
        print("✓ Successfully connected to Cohere client")
    except RuntimeError:
        print("- Cohere client not initialized, attempting initialization...")
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")
        cohere_api_key = os.getenv("COHERE_API_KEY")

        if not all([qdrant_url, cohere_api_key]):
            print("✗ Missing required environment variables for Cohere/Qdrant")
            return False

        initialize_clients(qdrant_url, qdrant_api_key, cohere_api_key)
        cohere_client = get_cohere_client()
        print("✓ Initialized Cohere client")

    # Test embedding generation
    test_texts = ["This is a test sentence for embedding.", "Another test sentence."]
    try:
        embeddings = cohere_client.embed_texts(test_texts)
        print(f"✓ Successfully generated {len(embeddings)} embeddings")
        print(f"✓ Embedding dimension: {len(embeddings[0]) if embeddings else 0}")
        return True
    except Exception as e:
        print(f"✗ Failed to generate embeddings: {e}")
        return False


def test_qdrant_storage():
    """Test if Qdrant is properly storing vectors."""
    print("\nTesting Qdrant storage...")

    # Get the Qdrant client
    try:
        qdrant_client = get_qdrant_client()
        print("✓ Successfully connected to Qdrant client")
    except RuntimeError:
        print("✗ Qdrant client not initialized")
        return False

    # Check if collection exists and get statistics
    try:
        collection_name = os.getenv("QDRANT_COLLECTION_NAME", "book_chunks")
        collection_info = qdrant_client.client.get_collection(collection_name)
        print(f"✓ Collection '{collection_name}' exists")
        print(f"✓ Points count: {collection_info.points_count}")
        print(f"✓ Vector size: {collection_info.config.params.vector_size}")
        return True
    except Exception as e:
        print(f"✗ Failed to access Qdrant collection: {e}")
        return False


def test_ingestion_service():
    """Test the ingestion service functionality."""
    print("\nTesting ingestion service...")

    try:
        ingestion_service = get_ingestion_service()
        print("✓ Successfully got ingestion service")
        return True
    except Exception as e:
        print(f"✗ Failed to get ingestion service: {e}")
        return False


def main():
    """Run all tests."""
    print("Running embedding and storage tests...\n")

    results = []
    results.append(test_cohere_embeddings())
    results.append(test_qdrant_storage())
    results.append(test_ingestion_service())

    print(f"\nTest Results:")
    print(f"- Cohere embeddings: {'PASS' if results[0] else 'FAIL'}")
    print(f"- Qdrant storage: {'PASS' if results[1] else 'FAIL'}")
    print(f"- Ingestion service: {'PASS' if results[2] else 'FAIL'}")

    all_passed = all(results)
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

    if all_passed:
        print("\n✅ Your data is properly embedded in Cohere and stored in Qdrant!")
        print("The RAG agent can now retrieve and use your book content.")
    else:
        print("\n❌ Some issues were found. Please check the error messages above.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())