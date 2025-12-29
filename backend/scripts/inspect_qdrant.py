#!/usr/bin/env python3
"""
Inspect Qdrant collections to understand what data is stored
"""
import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load environment
backend_dir = os.path.dirname(os.path.dirname(__file__))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(dotenv_path=env_path)

def main():
    # Get credentials from environment
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")

    if not all([qdrant_url, qdrant_api_key]):
        print("❌ Error: Missing QDRANT_URL or QDRANT_API_KEY")
        return 1

    print(f"🔍 Connecting to Qdrant at {qdrant_url}...")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # List all collections
    print("\n📦 Collections in Qdrant:")
    print("=" * 80)
    collections = client.get_collections()

    for collection in collections.collections:
        print(f"\n Collection: {collection.name}")

        # Get collection details
        try:
            info = client.get_collection(collection_name=collection.name)
            print(f"   - Points count: {info.points_count}")
            print(f"   - Vector size: {info.config.params.vectors.size}")
            print(f"   - Distance: {info.config.params.vectors.distance}")

            # Get a sample point to see payload structure
            if info.points_count > 0:
                print(f"\n   📄 Sample points from '{collection.name}':")
                sample = client.scroll(
                    collection_name=collection.name,
                    limit=3,
                    with_payload=True,
                    with_vectors=False
                )

                for idx, point in enumerate(sample[0][:3], 1):
                    print(f"\n   Point {idx} (ID: {point.id}):")
                    payload = point.payload

                    # Show payload keys
                    print(f"      Payload keys: {list(payload.keys())}")

                    # Show content preview
                    if 'content' in payload:
                        content_preview = payload['content'][:100] + "..." if len(payload['content']) > 100 else payload['content']
                        print(f"      Content: {content_preview}")
                        print(f"      Chapter: {payload.get('chapter', 'N/A')}")
                        print(f"      Section: {payload.get('section', 'N/A')}")
                    elif 'text_content' in payload:
                        content_preview = payload['text_content'][:100] + "..." if len(payload['text_content']) > 100 else payload['text_content']
                        print(f"      Text Content: {content_preview}")
                        doc_meta = payload.get('document_metadata', {})
                        print(f"      Source URL: {doc_meta.get('source_url', 'N/A')}")
                        print(f"      Document ID: {payload.get('document_id', 'N/A')}")

        except Exception as e:
            print(f"   ⚠️  Error getting collection info: {e}")

        print("   " + "-" * 76)

    # Check which collection is configured in settings
    print("\n⚙️  Configuration:")
    print("=" * 80)
    print(f"QDRANT_COLLECTION_NAME from .env: {os.getenv('QDRANT_COLLECTION_NAME')}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
