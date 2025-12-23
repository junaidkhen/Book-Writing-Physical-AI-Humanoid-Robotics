import pytest
from unittest.mock import AsyncMock, patch
from src.agents.rag_agent import RAGAgent
from src.services.retrieval_service import retrieve_chunks
from src.schemas.response_schemas import RetrievedChunk, ChunkMetadata


@pytest.mark.asyncio
async def test_agent_retrieval_integration():
    """Test the integration between agent and retrieval service."""
    agent = RAGAgent()

    # Mock the retrieval service to return specific chunks
    with patch('src.agents.rag_agent.retrieve_chunks') as mock_retrieve:
        mock_chunk = RetrievedChunk(
            chunk_id="test_chunk_1",
            content="This is test content from the textbook about humanoid robotics.",
            metadata=ChunkMetadata(
                chapter="Chapter 3",
                section="Section 3.2",
                source_document="humanoid_robotics_textbook"
            ),
            score=0.85
        )
        mock_retrieve.return_value = ([mock_chunk], 15.0)  # chunks, retrieval_time

        # Mock the OpenAI client to avoid actual API calls
        with patch.object(agent, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.choices = [AsyncMock()]
            mock_response.choices[0].message.content = '{"answer": "Based on the textbook, humanoid robots have specific design principles.", "reasoning": ["Found relevant content", "Generated response"]}'
            mock_response.usage = AsyncMock()
            mock_response.usage.prompt_tokens = 120
            mock_response.usage.completion_tokens = 60
            mock_response.usage.total_tokens = 180
            mock_client.chat.completions.create.return_value = mock_response

            # Call the agent's query method
            answer, citations, reasoning, metadata = await agent.query("What are humanoid robots?", top_k=1)

            # Verify the results
            assert "humanoid robots" in answer.lower()
            assert len(citations) == 1
            assert citations[0].chunk_id == "test_chunk_1"
            assert metadata.chunks_retrieved == 1
            assert metadata.token_usage.total_tokens == 180


@pytest.mark.asyncio
async def test_retrieve_chunks_integration():
    """Test the retrieval service function."""
    # This would require an actual Qdrant instance to test fully
    # For now, we'll test the structure and error handling
    with patch('src.services.retrieval_service.qdrant_client') as mock_client:
        mock_result = AsyncMock()
        mock_result.points = [
            type('obj', (object,), {
                'id': 'chunk1',
                'payload': {
                    'content': 'Sample content for testing',
                    'chapter': 'Chapter 1',
                    'section': 'Section 1.1',
                    'source_document': 'test_doc'
                },
                'score': 0.9
            })()
        ]
        mock_client.query_points.return_value = mock_result

        chunks, retrieval_time = await retrieve_chunks("test query", top_k=1)

        assert len(chunks) == 1
        assert chunks[0].content == 'Sample content for testing'
        assert chunks[0].score == 0.9
        assert retrieval_time >= 0  # Time should be non-negative