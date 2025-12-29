#!/usr/bin/env python3
"""
Analyze collection for duplicates and quality issues
"""
import os
import sys
from collections import defaultdict
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
    collection_name = os.getenv("QDRANT_COLLECTION_NAME", "documents")

    if not all([qdrant_url, qdrant_api_key]):
        print("❌ Error: Missing environment variables")
        return 1

    print(f"🔍 Analyzing collection: '{collection_name}'")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)

    # Get collection info
    info = client.get_collection(collection_name)
    total_points = info.points_count
    print(f"📊 Total points: {total_points}")

    # Scroll through all points
    print(f"\n📥 Fetching all points...")
    all_points = []
    offset = None

    while True:
        result = client.scroll(
            collection_name=collection_name,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False
        )

        points, next_offset = result
        all_points.extend(points)

        if next_offset is None:
            break
        offset = next_offset

    print(f"✅ Fetched {len(all_points)} points")

    # Analyze duplicates by text_content
    print(f"\n🔎 Analyzing for duplicate content...")
    content_hash_map = defaultdict(list)
    ui_text_count = 0
    short_chunks = 0
    empty_chunks = 0

    for point in all_points:
        payload = point.payload
        text_content = payload.get('text_content') or payload.get('content', '')

        # Check for duplicates
        content_hash = hash(text_content)
        content_hash_map[content_hash].append(point.id)

        # Check for UI text contamination
        ui_keywords = ['Skip to main content', 'GitHub', 'Introduction', 'Textbook']
        if any(keyword in text_content for keyword in ui_keywords) and len(text_content) < 200:
            ui_text_count += 1

        # Check for short chunks
        if len(text_content) < 100:
            short_chunks += 1

        # Check for empty chunks
        if not text_content.strip():
            empty_chunks += 1

    # Find duplicates
    duplicates = {k: v for k, v in content_hash_map.items() if len(v) > 1}

    print(f"\n📈 Analysis Results:")
    print("=" * 80)
    print(f"Total points: {len(all_points)}")
    print(f"Unique content: {len(content_hash_map)}")
    print(f"Duplicate content groups: {len(duplicates)}")
    print(f"Total duplicate points: {sum(len(v) - 1 for v in duplicates.values())}")
    print(f"UI text contamination: {ui_text_count} chunks")
    print(f"Short chunks (<100 chars): {short_chunks}")
    print(f"Empty chunks: {empty_chunks}")

    # Show sample duplicates
    if duplicates:
        print(f"\n🔍 Sample duplicate groups (showing first 3):")
        for idx, (content_hash, point_ids) in enumerate(list(duplicates.items())[:3], 1):
            print(f"\nDuplicate group {idx}: {len(point_ids)} copies")
            # Get one point to show content
            sample_point = next(p for p in all_points if p.id == point_ids[0])
            content = sample_point.payload.get('text_content') or sample_point.payload.get('content', '')
            content_preview = content[:100] + "..." if len(content) > 100 else content
            print(f"   Content: {content_preview}")
            print(f"   Point IDs: {point_ids[:3]}...")

    # Show samples of UI text contamination
    print(f"\n🔍 Sample UI text contamination:")
    ui_samples = [p for p in all_points if any(keyword in (p.payload.get('text_content') or p.payload.get('content', '')) for keyword in ['Skip to main content', 'GitHub']) and len(p.payload.get('text_content') or p.payload.get('content', '')) < 200][:3]

    for idx, point in enumerate(ui_samples, 1):
        content = point.payload.get('text_content') or point.payload.get('content', '')
        print(f"\n{idx}. {content}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
