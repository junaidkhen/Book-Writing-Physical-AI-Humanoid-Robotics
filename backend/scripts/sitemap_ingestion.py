#!/usr/bin/env python3
"""
Sitemap Ingestion Script

This script fetches URLs from a sitemap.xml file and ingests the content
into Qdrant vector database using Cohere embeddings.
"""

import os
import sys
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse
import time
from dotenv import load_dotenv

# Add the backend directory to the path so we can import our modules
backend_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from src.services.ingestion import IngestionService
from src.services.storage import initialize_clients
from src.utils.logging_config import get_logger

# Load environment variables
load_dotenv()

logger = get_logger(__name__)


def fetch_sitemap_urls(sitemap_url: str) -> List[str]:
    """
    Fetch all URLs from a sitemap.xml file.

    Args:
        sitemap_url: URL to the sitemap.xml file

    Returns:
        List of URLs extracted from the sitemap
    """
    logger.info(f"Fetching sitemap from: {sitemap_url}")

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()

        # Parse the XML
        root = ET.fromstring(response.content)

        # Handle different sitemap formats (with or without namespaces)
        namespace = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Find all URL elements
        urls = []
        for url_element in root.findall('.//sitemap:url/sitemap:loc', namespace):
            if url_element is not None:
                urls.append(url_element.text.strip())

        # If the above didn't work, try without namespace
        if not urls:
            for url_element in root.findall('.//url/loc'):
                if url_element is not None:
                    urls.append(url_element.text.strip())

        # Fix URLs if they contain the placeholder domain
        fixed_urls = []
        for url in urls:
            # Replace placeholder domain with the actual domain if needed
            fixed_url = url.replace("your-docusaurus-site.example.com", "book-writing-physical-ai-humanoid-r.vercel.app")
            fixed_urls.append(fixed_url)

        logger.info(f"Found {len(urls)} URLs in sitemap, fixed to {len(fixed_urls)} actual URLs")
        return fixed_urls

    except Exception as e:
        logger.error(f"Failed to fetch or parse sitemap: {e}")
        raise


def extract_content_from_url(url: str) -> tuple[str, str]:
    """
    Extract text content from a given URL using the existing extraction service.

    Args:
        url: URL to extract text from

    Returns:
        Tuple of (extracted text content, content type)
    """
    logger.info(f"Extracting content from: {url}")

    try:
        # Use the existing extraction service
        from src.services.extraction import extract_text_from_url as service_extract_text_from_url
        text_content, content_type = service_extract_text_from_url(url)

        logger.info(f"Extracted {len(text_content)} characters from {url} (type: {content_type})")
        return text_content, content_type

    except Exception as e:
        logger.error(f"Failed to extract content from {url}: {e}")
        return "", "html"  # Return empty content with default type


def create_temp_file(content: str, url: str, content_type: str = "html") -> str:
    """
    Create a temporary file with the extracted content.

    Args:
        content: Content to write to file
        url: Original URL for naming
        content_type: Type of content ('html', 'pdf', etc.)

    Returns:
        Path to the temporary file
    """
    import tempfile
    import re

    # Map content types to file extensions
    ext_map = {
        'html': '.html',
        'pdf': '.pdf',
        'txt': '.txt',
        'docx': '.docx'
    }

    ext = ext_map.get(content_type, '.html')

    # Create a safe filename from the URL
    safe_name = re.sub(r'[^a-zA-Z0-9]', '_', urlparse(url).path.replace('/', '_'))
    if not safe_name:
        safe_name = "content"

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False, encoding='utf-8') as f:
        f.write(content)
        temp_path = f.name

    return temp_path


def main():
    """
    Main function to run the sitemap ingestion process.
    """
    logger.info("Starting sitemap ingestion process")

    # Get configuration from environment
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    cohere_api_key = os.getenv("COHERE_API_KEY")
    sitemap_url = os.getenv("SITEMAP_URL")

    if not all([qdrant_url, qdrant_api_key, cohere_api_key, sitemap_url]):
        logger.error("Missing required environment variables")
        print("Error: Please set QDRANT_URL, QDRANT_API_KEY, COHERE_API_KEY, and SITEMAP_URL in your .env file")
        return 1

    try:
        # Initialize the storage clients
        logger.info("Initializing Qdrant and Cohere clients")
        initialize_clients(qdrant_url, qdrant_api_key, cohere_api_key)

        # Create ingestion service
        ingestion_service = IngestionService()

        # Fetch URLs from sitemap
        urls = fetch_sitemap_urls(sitemap_url)

        if not urls:
            logger.warning("No URLs found in sitemap")
            return 0

        # Process each URL
        successful_ingests = 0
        failed_ingests = 0

        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}: {url}")

            try:
                # Extract content from the URL
                content, content_type = extract_content_from_url(url)

                if not content.strip():
                    logger.warning(f"No content extracted from {url}")
                    failed_ingests += 1
                    continue

                # Create a temporary file with the content
                temp_file_path = create_temp_file(content, url, content_type)

                try:
                    # Ingest the content using the existing ingestion service
                    success, error_msg, document = ingestion_service.ingest_single_document(
                        temp_file_path,
                        source_url=url
                    )

                    if success:
                        logger.info(f"Successfully ingested {url}")
                        successful_ingests += 1
                    else:
                        logger.error(f"Failed to ingest {url}: {error_msg}")
                        failed_ingests += 1

                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            except Exception as e:
                logger.error(f"Error processing {url}: {e}")
                failed_ingests += 1

            # Add a small delay to be respectful to the server
            time.sleep(1)

        logger.info(f"Ingestion completed: {successful_ingests} successful, {failed_ingests} failed")
        print(f"\nSitemap ingestion completed!")
        print(f"- Successfully ingested: {successful_ingests} URLs")
        print(f"- Failed to ingest: {failed_ingests} URLs")
        print(f"- Total processed: {len(urls)} URLs")

        return 0

    except Exception as e:
        logger.error(f"Fatal error during ingestion: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())