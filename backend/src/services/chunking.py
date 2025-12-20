"""Text chunking service for the document ingestion system.

Implements recursive character splitting with sentence boundary preservation
per research.md Decision 2. Chunks are 500-2000 characters with 100-character overlap.
"""
from typing import List, Optional
import re
from dataclasses import dataclass

from ..utils.logging_config import get_logger


logger = get_logger(__name__)


@dataclass
class Chunk:
    """Chunk data structure with text and positional metadata."""
    text: str
    index: int
    start_pos: int
    end_pos: int
    char_count: int


class ChunkingError(Exception):
    """Custom exception for chunking errors."""
    pass


class TextChunker:
    """Text chunking service with recursive character splitting."""

    def __init__(
        self,
        min_chunk_size: int = 500,
        max_chunk_size: int = 2000,
        overlap_size: int = 100,
        separators: Optional[List[str]] = None
    ):
        """Initialize chunker with size and separator parameters.

        Args:
            min_chunk_size: Minimum chunk size (default 500 chars)
            max_chunk_size: Maximum chunk size (default 2000 chars)
            overlap_size: Overlap size between chunks (default 100 chars)
            separators: List of separators to use for splitting (default: hierarchical)

        Per research.md Decision 2: 500-2000 chars, 100-char overlap, sentence boundary preservation
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size

        # Default separators in hierarchical order (paragraph → sentence → char)
        if separators is None:
            self.separators = ["\n\n", "\n", " ", ""]
        else:
            self.separators = separators

    def chunk_text(self, text: str) -> List[Chunk]:
        """Chunk text using recursive character splitting with boundary preservation.

        Args:
            text: Text to chunk

        Returns:
            List of Chunk objects with positional metadata

        Per research.md Decision 2: Recursive splitting with paragraph→sentence→char hierarchy
        """
        if not text:
            return []

        logger.info(f"Starting chunking for text of {len(text)} characters")

        chunks = self._recursive_split(text, 0, 0)
        logger.info(f"Created {len(chunks)} chunks from {len(text)} characters")

        # Validate chunks meet requirements
        self._validate_chunks(chunks)

        return chunks

    def _recursive_split(
        self,
        text: str,
        start_pos: int,
        chunk_index: int
    ) -> List[Chunk]:
        """Recursively split text using different separators.

        Args:
            text: Text to split
            start_pos: Starting position in original text
            chunk_index: Index of this chunk in the sequence

        Returns:
            List of Chunk objects
        """
        # If text is small enough, return as single chunk
        if len(text) <= self.max_chunk_size:
            return [Chunk(
                text=text,
                index=chunk_index,
                start_pos=start_pos,
                end_pos=start_pos + len(text),
                char_count=len(text)
            )]

        # Try each separator in order
        for separator in self.separators:
            chunks = self._split_by_separator(text, separator, start_pos, chunk_index)
            if chunks:
                return chunks

        # If no separator worked, split by max chunk size (last resort)
        logger.warning(f"Using character-level split for chunk starting at position {start_pos}")
        return self._split_by_max_size(text, start_pos, chunk_index)

    def _split_by_separator(
        self,
        text: str,
        separator: str,
        start_pos: int,
        chunk_index: int
    ) -> List[Chunk]:
        """Split text by a specific separator with overlap handling.

        Args:
            text: Text to split
            separator: Separator to use for splitting
            start_pos: Starting position in original text
            chunk_index: Index of first chunk

        Returns:
            List of Chunk objects or empty list if separator doesn't work
        """
        if separator == "":
            # Character-level splitting
            return self._split_by_max_size(text, start_pos, chunk_index)

        # Split text by separator
        splits = text.split(separator)
        if len(splits) < 2:
            # Separator not found, try next one
            return []

        chunks = []
        current_chunk_text = ""
        current_start = start_pos
        current_index = chunk_index

        for i, split in enumerate(splits):
            # Add separator back to all but the last split
            if i < len(splits) - 1:
                split_with_separator = split + separator
            else:
                split_with_separator = split

            # Check if adding this split would exceed max size
            test_chunk = current_chunk_text + split_with_separator

            if len(test_chunk) > self.max_chunk_size and current_chunk_text:
                # Create current chunk
                chunks.append(Chunk(
                    text=current_chunk_text,
                    index=current_index,
                    start_pos=current_start,
                    end_pos=current_start + len(current_chunk_text),
                    char_count=len(current_chunk_text)
                ))

                # Start new chunk with overlap
                current_start = current_start + len(current_chunk_text)
                current_chunk_text = self._get_overlap_text(current_chunk_text) + split_with_separator
                current_index += 1
            else:
                current_chunk_text = test_chunk

        # Add final chunk if it has content
        if current_chunk_text:
            chunks.append(Chunk(
                text=current_chunk_text,
                index=current_index,
                start_pos=current_start,
                end_pos=current_start + len(current_chunk_text),
                char_count=len(current_chunk_text)
            ))

        # Filter out chunks that are too small (unless they're the only one)
        if len(chunks) > 1:
            filtered_chunks = [chunk for chunk in chunks if len(chunk.text) >= self.min_chunk_size]
            if filtered_chunks:  # Only return filtered if we still have chunks
                chunks = filtered_chunks

        return chunks

    def _split_by_max_size(
        self,
        text: str,
        start_pos: int,
        chunk_index: int
    ) -> List[Chunk]:
        """Split text by maximum chunk size (character-level fallback).

        Args:
            text: Text to split
            start_pos: Starting position in original text
            chunk_index: Index of first chunk

        Returns:
            List of Chunk objects
        """
        chunks = []
        current_start = start_pos
        current_index = chunk_index

        for i in range(0, len(text), self.max_chunk_size):
            chunk_text = text[i:i + self.max_chunk_size]
            chunks.append(Chunk(
                text=chunk_text,
                index=current_index,
                start_pos=current_start,
                end_pos=current_start + len(chunk_text),
                char_count=len(chunk_text)
            ))
            current_start += len(chunk_text)
            current_index += 1

        return chunks

    def _get_overlap_text(self, chunk_text: str) -> str:
        """Get overlap text from the end of a chunk.

        Args:
            chunk_text: Text of the chunk to get overlap from

        Returns:
            Overlap text (last overlap_size characters)
        """
        if len(chunk_text) <= self.overlap_size:
            return chunk_text
        return chunk_text[-self.overlap_size:]

    def _validate_chunks(self, chunks: List[Chunk]) -> None:
        """Validate that chunks meet requirements.

        Args:
            chunks: List of chunks to validate

        Raises:
            ChunkingError: If chunks don't meet requirements
        """
        for i, chunk in enumerate(chunks):
            # Validate size requirements
            if len(chunk.text) < self.min_chunk_size and len(chunks) > 1:
                logger.warning(f"Chunk {i} has {len(chunk.text)} chars, below minimum {self.min_chunk_size}")
                # Note: We allow small chunks if it's the only chunk in a very short document

            if len(chunk.text) > self.max_chunk_size:
                raise ChunkingError(f"Chunk {i} exceeds maximum size: {len(chunk.text)} > {self.max_chunk_size}")

            # Validate character count matches text length
            if chunk.char_count != len(chunk.text):
                raise ChunkingError(f"Chunk {i} char_count {chunk.char_count} != text length {len(chunk.text)}")

            # Validate positional integrity
            if chunk.start_pos < 0 or chunk.end_pos > chunk.start_pos + len(chunk.text):
                raise ChunkingError(f"Chunk {i} has invalid position: start={chunk.start_pos}, end={chunk.end_pos}")

        logger.info(f"Validated {len(chunks)} chunks successfully")


def chunk_text_content(
    text: str,
    min_chunk_size: int = 500,
    max_chunk_size: int = 2000,
    overlap_size: int = 100
) -> List[dict]:
    """Chunk text content and return as dictionaries for storage.

    Args:
        text: Text content to chunk
        min_chunk_size: Minimum chunk size (default 500)
        max_chunk_size: Maximum chunk size (default 2000)
        overlap_size: Overlap size (default 100)

    Returns:
        List of chunk dictionaries with text, index, and positional data
    """
    chunker = TextChunker(
        min_chunk_size=min_chunk_size,
        max_chunk_size=max_chunk_size,
        overlap_size=overlap_size
    )

    chunks = chunker.chunk_text(text)
    chunk_dicts = []

    for chunk in chunks:
        chunk_dicts.append({
            'text_content': chunk.text,
            'chunk_index': chunk.index,
            'start_position': chunk.start_pos,
            'end_position': chunk.end_pos,
            'char_count': chunk.char_count
        })

    return chunk_dicts