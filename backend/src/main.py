from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config.settings import settings
from .utils.logging import logger
from .clients.qdrant_client import qdrant_client, check_collection_exists
from .clients.openai_client import openai_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for initializing and cleaning up resources."""
    # Startup
    logger.info("Starting up RAG-Enabled Agent Service")

    # Verify Qdrant connection and collection exists
    if not check_collection_exists(settings.qdrant_collection_name):
        logger.warning(f"Qdrant collection '{settings.qdrant_collection_name}' does not exist. Service may not function properly.")
    else:
        logger.info(f"Successfully connected to Qdrant collection: {settings.qdrant_collection_name}")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down RAG-Enabled Agent Service")


def create_app():
    app = FastAPI(
        title="RAG-Enabled Agent Service",
        description="API for RAG-based question answering from Physical AI & Humanoid Robotics textbook",
        version="0.1.0",
        lifespan=lifespan,
        debug=settings.debug
    )

    # Add CORS middleware for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify exact origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        # Expose custom headers for client-side access
        expose_headers=["X-Request-ID"]
    )

    # Import and include API routes
    from .api.v1.endpoints import ask, retrieve, health, metadata
    from .routers import chat
    app.include_router(ask.router, prefix="/api/v1", tags=["ask"])
    app.include_router(retrieve.router, prefix="/api/v1", tags=["retrieve"])
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(metadata.router, prefix="/api/v1", tags=["metadata"])
    app.include_router(chat.router, tags=["chat"])

    @app.get("/")
    async def root():
        """
        Root endpoint for basic service information.
        """
        return {
            "message": "RAG-Enabled Agent Service",
            "version": "0.1.0",
            "status": "running"
        }

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True if settings.debug else False,
        log_level="info" if settings.debug else "warning"
    )