"""Performance tests for chunking service.

Verifies chunking performance meets research.md benchmark: >1MB/s text processing.
"""
import time
import pytest
from backend.src.services.chunking import chunk_text_content


def test_chunking_performance_benchmark():
    """Test that chunking service processes >1MB/s text."""
    # Create a large text sample (2MB)
    large_text = "This is a test sentence. " * (2 * 1024 * 1024 // 25)  # Approximately 2MB

    start_time = time.time()

    # Process the large text
    chunks = chunk_text_content(large_text)

    end_time = time.time()
    processing_time = end_time - start_time
    text_size_mb = len(large_text) / (1024 * 1024)  # Size in MB
    processing_speed = text_size_mb / processing_time if processing_time > 0 else float('inf')

    print(f"Processed {text_size_mb:.2f}MB in {processing_time:.2f}s")
    print(f"Speed: {processing_speed:.2f}MB/s")
    print(f"Generated {len(chunks)} chunks")

    # Verify performance meets requirement (>1MB/s)
    assert processing_speed > 1.0, f"Chunking performance too slow: {processing_speed:.2f}MB/s, required >1MB/s"


def test_chunking_performance_small_text():
    """Test chunking performance with smaller text."""
    # Create a smaller text sample (100KB)
    medium_text = "This is a test sentence for medium text processing. " * (100 * 1024 // 50)  # Approximately 100KB

    start_time = time.time()

    # Process the text
    chunks = chunk_text_content(medium_text)

    end_time = time.time()
    processing_time = end_time - start_time
    text_size_kb = len(medium_text) / 1024  # Size in KB
    processing_speed = (text_size_kb / 1024) / processing_time if processing_time > 0 else float('inf')  # Convert to MB/s

    print(f"Processed {text_size_kb:.2f}KB in {processing_time:.2f}s")
    print(f"Speed: {processing_speed:.2f}MB/s")
    print(f"Generated {len(chunks)} chunks")

    # Even for smaller texts, we should have reasonable performance
    assert len(chunks) > 0, "Should generate at least one chunk"


def test_chunking_performance_various_sizes():
    """Test chunking performance with various text sizes."""
    test_sizes = [
        (10 * 1024, "10KB"),      # 10KB
        (100 * 1024, "100KB"),    # 100KB
        (500 * 1024, "500KB"),    # 500KB
        (1024 * 1024, "1MB"),     # 1MB
    ]

    for size_bytes, size_label in test_sizes:
        text = f"This is test content for {size_label} performance evaluation. " * (size_bytes // 60)

        start_time = time.time()
        chunks = chunk_text_content(text)
        end_time = time.time()

        processing_time = end_time - start_time
        text_size_mb = len(text) / (1024 * 1024)
        processing_speed = text_size_mb / processing_time if processing_time > 0 else float('inf')

        print(f"{size_label}: {processing_speed:.2f}MB/s ({len(chunks)} chunks)")

        # Verify we got chunks
        assert len(chunks) > 0, f"Should generate chunks for {size_label} text"


if __name__ == "__main__":
    pytest.main([__file__])