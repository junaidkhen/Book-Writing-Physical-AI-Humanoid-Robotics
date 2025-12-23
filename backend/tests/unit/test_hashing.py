"""Unit tests for content hashing utility

Tests per T010 requirements:
- Text normalization (lowercase, whitespace collapse)
- Collision resistance (unique hashes for different content)
- Performance (<0.1s per document)
"""

import pytest
import time
from backend.src.utils.hashing import generate_content_hash, verify_content_hash


class TestContentHashing:
    """Test suite for SHA-256 content hashing"""

    def test_basic_hash_generation(self):
        """Test basic hash generation produces 64-char hex string"""
        text = "Hello World"
        hash_result = generate_content_hash(text)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_normalization_lowercase(self):
        """Test that case differences produce same hash"""
        text1 = "Hello World"
        text2 = "hello world"
        text3 = "HELLO WORLD"

        hash1 = generate_content_hash(text1)
        hash2 = generate_content_hash(text2)
        hash3 = generate_content_hash(text3)

        assert hash1 == hash2 == hash3

    def test_normalization_whitespace(self):
        """Test that whitespace differences produce same hash"""
        text1 = "Hello World"
        text2 = "Hello   World"  # Multiple spaces
        text3 = "  Hello World  "  # Leading/trailing spaces
        text4 = "Hello\n\tWorld"  # Newlines and tabs

        hash1 = generate_content_hash(text1)
        hash2 = generate_content_hash(text2)
        hash3 = generate_content_hash(text3)
        hash4 = generate_content_hash(text4)

        assert hash1 == hash2 == hash3 == hash4

    def test_collision_resistance_different_content(self):
        """Test that different content produces different hashes"""
        text1 = "This is the first document"
        text2 = "This is the second document"
        text3 = "Completely different content"

        hash1 = generate_content_hash(text1)
        hash2 = generate_content_hash(text2)
        hash3 = generate_content_hash(text3)

        # All hashes should be unique
        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3

    def test_collision_resistance_similar_content(self):
        """Test that similar but not identical content produces different hashes"""
        text1 = "Physical AI and Humanoid Robotics"
        text2 = "Physical AI and Humanoid Robotic"  # Missing 's'
        text3 = "Physical AI and Humanoids Robotics"  # Extra 's'

        hash1 = generate_content_hash(text1)
        hash2 = generate_content_hash(text2)
        hash3 = generate_content_hash(text3)

        assert hash1 != hash2
        assert hash1 != hash3
        assert hash2 != hash3

    def test_deterministic_hashing(self):
        """Test that same input always produces same hash"""
        text = "Deterministic hash test"

        hash1 = generate_content_hash(text)
        hash2 = generate_content_hash(text)
        hash3 = generate_content_hash(text)

        assert hash1 == hash2 == hash3

    def test_empty_string(self):
        """Test hashing empty string"""
        hash_result = generate_content_hash("")

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64

    def test_unicode_content(self):
        """Test hashing Unicode content"""
        text = "Physical AI: 物理AI and Robotics 🤖"
        hash_result = generate_content_hash(text)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64

    def test_large_document(self):
        """Test hashing large document (realistic size)"""
        # Simulate 100-page document (~250,000 characters)
        large_text = "This is a sentence from a textbook. " * 7000

        hash_result = generate_content_hash(large_text)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64

    def test_performance_benchmark(self):
        """Test that hashing performance is <0.1s per document"""
        # Test with realistic document size (100 pages ~ 250K chars)
        text = "Physical AI and Humanoid Robotics textbook content. " * 5000

        start_time = time.time()
        hash_result = generate_content_hash(text)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 0.1, f"Hashing took {elapsed_time:.3f}s, expected <0.1s"
        assert len(hash_result) == 64

    def test_verify_content_hash_valid(self):
        """Test hash verification with matching content"""
        text = "Hello World"
        expected_hash = generate_content_hash(text)

        assert verify_content_hash(text, expected_hash) is True

    def test_verify_content_hash_invalid(self):
        """Test hash verification with non-matching content"""
        text = "Hello World"
        wrong_hash = generate_content_hash("Different Text")

        assert verify_content_hash(text, wrong_hash) is False

    def test_verify_content_hash_normalized(self):
        """Test hash verification handles normalization"""
        text1 = "Hello World"
        text2 = "hello   world"  # Different case and whitespace
        expected_hash = generate_content_hash(text1)

        # Both should verify against the same hash due to normalization
        assert verify_content_hash(text2, expected_hash) is True


class TestHashingEdgeCases:
    """Test edge cases for content hashing"""

    def test_very_long_whitespace(self):
        """Test handling of very long whitespace sequences"""
        text = "Hello" + (" " * 1000) + "World"
        hash_result = generate_content_hash(text)

        # Should normalize to single space
        expected_hash = generate_content_hash("Hello World")
        assert hash_result == expected_hash

    def test_only_whitespace(self):
        """Test hashing text with only whitespace"""
        text = "     \n\t\n\t     "
        hash_result = generate_content_hash(text)

        # Should normalize to empty string
        expected_hash = generate_content_hash("")
        assert hash_result == expected_hash

    def test_special_characters(self):
        """Test hashing text with special characters"""
        text = "Email: test@example.com, Price: $100.00, Symbol: &@#!"
        hash_result = generate_content_hash(text)

        assert len(hash_result) == 64
        # Verify deterministic
        assert hash_result == generate_content_hash(text)

    def test_newlines_and_paragraphs(self):
        """Test that paragraph structure is normalized"""
        text1 = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        text2 = "Paragraph one. Paragraph two. Paragraph three."

        hash1 = generate_content_hash(text1)
        hash2 = generate_content_hash(text2)

        # Whitespace normalization should make these equal
        assert hash1 == hash2
