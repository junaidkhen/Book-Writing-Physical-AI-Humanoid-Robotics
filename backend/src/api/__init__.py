"""API package for the document ingestion system."""
from .endpoints import router
from . import ingestion_schemas

__all__ = ['router', 'ingestion_schemas']
