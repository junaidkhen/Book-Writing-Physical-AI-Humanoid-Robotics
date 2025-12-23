from setuptools import setup, find_packages

setup(
    name="rag-agent-service",
    version="0.1.0",
    description="RAG-Enabled Agent Service for Physical AI & Humanoid Robotics Textbook",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi==0.115.0",
        "uvicorn[standard]==0.36.0",
        "openai==1.55.0",
        "qdrant-client==1.12.0",
        "cohere==5.20.0",
        "python-dotenv==1.0.1",
        "pydantic==2.10.0",
        "pydantic-settings==2.7.0",
        "beautifulsoup4==4.14.3",
        "requests==2.32.3",
        "pytest==8.3.5",
        "pytest-asyncio==0.25.0",
        "httpx==0.28.1",
        "python-multipart==0.0.20",
    ],
    extras_require={
        "dev": [
            "black==24.10.0",
            "flake8==7.1.1",
            "mypy==1.13.0",
        ]
    },
    python_requires=">=3.11",
)