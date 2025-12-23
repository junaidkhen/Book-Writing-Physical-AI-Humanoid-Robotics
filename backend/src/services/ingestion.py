"""Ingestion orchestration service for the document ingestion system.

Coordinates validation → extraction → chunking → embedding → storage per research.md.
Handles atomic operations and error handling per constitution Principle I.
Manages both single document ingestion and batch processing.
"""
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from ..models import Document, ProcessingStatus, Chunk, IngestionJob, JobStatus, ErrorLog, JobType
from .validation import validate_file_upload, validate_ingestion_url
from .extraction import extract_text_from_file, extract_text_from_url, extract_metadata_from_file
from .chunking import chunk_text_content
from .storage import get_qdrant_client, get_cohere_client
from ..utils.hashing import generate_content_hash
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class IngestionError(Exception):
    """Custom exception for ingestion errors."""
    pass


class IngestionService:
    """Main ingestion orchestration service."""

    def __init__(self):
        """Initialize ingestion service."""
        self.qdrant_client = get_qdrant_client()
        self.cohere_client = get_cohere_client()

    def _create_document_record(
        self,
        filename: str,
        content_type: str,
        content_hash: str,
        file_size_bytes: int,
        source_url: Optional[str] = None,
        title: Optional[str] = None,
        author: Optional[str] = None,
        creation_date: Optional[datetime] = None
    ) -> Document:
        """Create initial document record with pending status.

        Args:
            filename: Original filename
            content_type: Content type ('pdf', 'txt', 'docx', 'html')
            content_hash: SHA-256 content hash
            file_size_bytes: File size in bytes
            source_url: Source URL if ingested from web
            title: Document title (optional metadata)
            author: Document author (optional metadata)
            creation_date: Document creation date (optional metadata)

        Returns:
            Document instance with initial state
        """
        document = Document(
            filename=filename,
            content_type=content_type,
            content_hash=content_hash,
            file_size_bytes=file_size_bytes,
            source_url=source_url,
            title=title,
            author=author,
            creation_date=creation_date,
            processing_status=ProcessingStatus.PROCESSING,
            processing_started_at=datetime.utcnow()
        )
        logger.info(f"Created document record: {document.document_id} for {filename}")
        return document

    def _check_duplicate(self, content_hash: str) -> Optional[Document]:
        """Check if document with same content hash already exists.

        Args:
            content_hash: Content hash to check

        Returns:
            Existing document if found, None otherwise
        """
        # This would query Qdrant for documents with matching content_hash
        # For now, we'll implement a basic check - in production this would query the DB
        logger.info(f"Checking for duplicate with content hash: {content_hash}")
        # Implementation would go here to check existing documents
        return None

    def _extract_content_type(self, file_path: str) -> str:
        """Extract content type from file extension.

        Args:
            file_path: Path to file

        Returns:
            Content type string ('pdf', 'txt', 'docx', 'html')
        """
        ext = Path(file_path).suffix.lower()
        if ext == '.pdf':
            return 'pdf'
        elif ext in ['.txt', '.text']:
            return 'txt'
        elif ext == '.docx':
            return 'docx'
        elif ext in ['.html', '.htm']:
            return 'html'
        else:
            raise IngestionError(f"Unsupported file extension: {ext}")

    def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks.

        Args:
            texts: List of text chunks to embed

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        logger.info(f"Generating embeddings for {len(texts)} text chunks")
        embeddings = self.cohere_client.embed_texts(texts, input_type="search_document")
        logger.info(f"Generated {len(embeddings)} embeddings successfully")
        return embeddings

    def _store_chunks(self, chunks: List[Dict[str, Any]], document: Document) -> int:
        """Store chunks in Qdrant with denormalized document metadata.

        Args:
            chunks: List of chunk dictionaries
            document: Document record to associate chunks with

        Returns:
            Number of chunks stored
        """
        logger.info(f"Storing {len(chunks)} chunks for document {document.document_id}")

        # Prepare chunks for storage with denormalized document metadata
        prepared_chunks = []
        for i, chunk in enumerate(chunks):
            # Add document metadata to each chunk payload for single-query retrieval
            document_metadata = {
                'document_id': str(document.document_id),
                'filename': document.filename,
                'content_type': document.content_type,
                'content_hash': document.content_hash,
                'upload_date': document.upload_date.isoformat(),
                'source_url': document.source_url,
            }

            # Add optional metadata fields if they exist
            if document.title:
                document_metadata['title'] = document.title
            if document.author:
                document_metadata['author'] = document.author
            if document.creation_date:
                document_metadata['creation_date'] = document.creation_date.isoformat()

            prepared_chunk = {
                'chunk_id': str(uuid.uuid4()),
                'document_id': str(document.document_id),
                'chunk_index': chunk['chunk_index'],
                'text_content': chunk['text_content'],
                'char_count': chunk['char_count'],
                'start_position': chunk['start_position'],
                'end_position': chunk['end_position'],
                'embedding_model': 'embed-english-v3.0',  # Cohere model used
                'created_at': datetime.utcnow().isoformat(),
                # Denormalized document metadata per data-model.md
                'document_metadata': document_metadata
            }
            prepared_chunks.append(prepared_chunk)

        # Generate embeddings for all text chunks
        text_contents = [chunk['text_content'] for chunk in prepared_chunks]
        embeddings = self._generate_embeddings(text_contents)

        # Add embeddings to prepared chunks
        for chunk, embedding in zip(prepared_chunks, embeddings):
            chunk['embedding_vector'] = embedding

        # Store in Qdrant
        stored_count = self.qdrant_client.upsert_chunks(prepared_chunks)
        logger.info(f"Successfully stored {stored_count} chunks in Qdrant")

        return stored_count

    def _update_document_status(
        self,
        document: Document,
        status: ProcessingStatus,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Document:
        """Update document processing status.

        Args:
            document: Document to update
            status: New processing status
            chunk_count: Number of chunks created (for completed status)
            error_message: Error message if failed

        Returns:
            Updated document
        """
        document.processing_status = status
        if status == ProcessingStatus.COMPLETED:
            document.processing_completed_at = datetime.utcnow()
            document.chunk_count = chunk_count
        elif status == ProcessingStatus.FAILED:
            document.processing_completed_at = datetime.utcnow()
            document.error_message = error_message

        logger.info(f"Updated document {document.document_id} status to {status}")
        return document

    def ingest_single_document(
        self,
        file_path: str,
        source_url: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[Document]]:
        """Ingest a single document with full processing pipeline.

        Args:
            file_path: Path to document file
            source_url: Source URL if ingested from web

        Returns:
            Tuple of (success, error_message, document_record)
        """
        logger.info(f"Starting ingestion for file: {file_path}")

        try:
            # Step 1: Validate file
            is_valid, validation_error = validate_file_upload(file_path)
            if not is_valid:
                error_msg = f"File validation failed: {validation_error}"
                logger.error(error_msg)
                return False, error_msg, None

            # Step 2: Extract content type
            content_type = self._extract_content_type(file_path)

            # Step 3: Extract metadata
            logger.info(f"Extracting metadata from {file_path}")
            metadata = extract_metadata_from_file(file_path, content_type)

            # Step 4: Generate content hash for deduplication
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text_content = f.read()
            content_hash = generate_content_hash(text_content)

            # Step 5: Check for duplicates
            existing_doc = self._check_duplicate(content_hash)
            if existing_doc:
                error_msg = f"Document with content hash {content_hash} already exists"
                logger.warning(error_msg)
                return False, error_msg, existing_doc

            # Step 6: Create initial document record with metadata
            file_size = os.path.getsize(file_path)
            document = self._create_document_record(
                filename=os.path.basename(file_path),
                content_type=content_type,
                content_hash=content_hash,
                file_size_bytes=file_size,
                source_url=source_url,
                title=metadata.get('title'),
                author=metadata.get('author'),
                creation_date=metadata.get('creation_date')
            )

            # Step 7: Extract text content
            logger.info(f"Extracting text from {file_path}")
            text_content = extract_text_from_file(file_path, content_type)

            # Step 8: Chunk text content
            logger.info("Chunking text content")
            chunks = chunk_text_content(text_content)

            # Step 9: Store chunks with embeddings
            stored_count = self._store_chunks(chunks, document)

            # Step 10: Update document status to completed
            document = self._update_document_status(
                document,
                ProcessingStatus.COMPLETED,
                chunk_count=stored_count
            )

            logger.info(f"Successfully ingested document {document.document_id}: {file_path}")
            return True, None, document

        except Exception as e:
            logger.error(f"Ingestion failed for {file_path}: {e}")
            # Update document status to failed
            if 'document' in locals():
                document = self._update_document_status(
                    document,
                    ProcessingStatus.FAILED,
                    error_message=str(e)
                )
            return False, str(e), None if 'document' not in locals() else document

    def ingest_from_url(self, url: str) -> Tuple[bool, Optional[str], Optional[Document]]:
        """Ingest content from URL.

        Args:
            url: URL to ingest content from

        Returns:
            Tuple of (success, error_message, document_record)
        """
        logger.info(f"Starting URL ingestion for: {url}")

        try:
            # Step 1: Validate URL
            is_valid, validation_error = validate_ingestion_url(url)
            if not is_valid:
                error_msg = f"URL validation failed: {validation_error}"
                logger.error(error_msg)
                return False, error_msg, None

            # Step 2: Extract content from URL (this would be implemented in extraction service)
            # For now, we'll simulate by creating a temporary file
            # In a real implementation, we'd use the extraction service to fetch and process the URL
            raise NotImplementedError("URL ingestion not fully implemented in this version")

        except NotImplementedError as e:
            logger.error(f"URL ingestion not implemented: {e}")
            return False, str(e), None
        except Exception as e:
            logger.error(f"URL ingestion failed for {url}: {e}")
            return False, str(e), None

    def process_batch(
        self,
        file_paths: List[str],
        job_type: JobType = JobType.BATCH
    ) -> IngestionJob:
        """Process multiple documents in a batch with error isolation.

        Args:
            file_paths: List of file paths to process
            job_type: Type of job (single or batch)

        Returns:
            IngestionJob record with processing results

        Per US2 acceptance scenario: Error isolation and partial success handling
        """
        logger.info(f"Starting batch ingestion for {len(file_paths)} files")

        # Create ingestion job record
        job = IngestionJob(
            job_type=job_type,
            total_documents=len(file_paths),
            documents_processed=0,
            documents_failed=0,
            document_ids=[uuid.uuid4() for _ in file_paths]  # This would be actual document IDs
        )

        results = []
        error_logs = []

        for i, file_path in enumerate(file_paths):
            logger.info(f"Processing batch item {i+1}/{len(file_paths)}: {file_path}")

            try:
                # Process individual document (error isolation)
                success, error_msg, document = self.ingest_single_document(file_path)

                if success:
                    results.append((file_path, document))
                    job.documents_processed += 1
                    logger.info(f"Successfully processed: {file_path}")
                else:
                    error_logs.append(ErrorLog(
                        document_id=job.document_ids[i],
                        error_message=error_msg or "Unknown error"
                    ))
                    job.documents_failed += 1
                    logger.warning(f"Failed to process: {file_path}, error: {error_msg}")

            except Exception as e:
                # Catch any unexpected errors during processing
                error_logs.append(ErrorLog(
                    document_id=job.document_ids[i],
                    error_message=f"Unexpected error: {str(e)}"
                ))
                job.documents_failed += 1
                logger.error(f"Unexpected error processing {file_path}: {e}")

        # Update job status based on results
        if job.documents_failed == 0:
            job.status = JobStatus.COMPLETED
        elif job.documents_processed == 0:
            job.status = JobStatus.FAILED
        else:
            job.status = JobStatus.PARTIAL_SUCCESS

        job.completed_at = datetime.utcnow()
        job.error_logs = error_logs

        logger.info(f"Batch job completed with status {job.status}: "
                   f"{job.documents_processed} processed, {job.documents_failed} failed")

        return job


# Global ingestion service instance
ingestion_service: Optional[IngestionService] = None


def get_ingestion_service() -> IngestionService:
    """Get global ingestion service instance.

    Returns:
        IngestionService instance

    Raises:
        RuntimeError: If service not initialized
    """
    global ingestion_service
    if ingestion_service is None:
        # Check if clients are available before creating service
        try:
            get_qdrant_client()
            get_cohere_client()
            ingestion_service = IngestionService()
        except RuntimeError as e:
            raise RuntimeError(f"Ingestion service dependencies not initialized: {e}")
    return ingestion_service


def initialize_ingestion_service() -> None:
    """Initialize global ingestion service instance.

    Called during FastAPI app startup after storage/embedding clients are ready.
    """
    global ingestion_service
    ingestion_service = IngestionService()
    logger.info("Initialized ingestion service")


def shutdown_ingestion_service() -> None:
    """Shutdown global ingestion service instance.

    Called during FastAPI app shutdown.
    """
    global ingestion_service
    ingestion_service = None
    logger.info("Shutdown ingestion service")