from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Qdrant Configuration
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "book_chunks"

    # Gemini API Configuration (via OpenAI-compatible endpoint)
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    # OpenAI Configuration (can be used as fallback if Gemini key not available)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"

    # Cohere Configuration
    cohere_api_key: Optional[str] = None

    # Sitemap and Book URLs
    sitemap_url: Optional[str] = None
    book_urls: Optional[str] = None

    # Application Configuration
    temperature: float = 0.1
    top_k: int = 5
    max_tokens: int = 500  # Updated to match requirement: maximum 500 tokens
    debug: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()