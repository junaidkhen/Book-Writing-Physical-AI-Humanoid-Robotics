import pytest
from unittest.mock import AsyncMock, patch
from src.agents.rag_agent import RAGAgent
from src.schemas.response_schemas import RetrievedChunk, ChunkMetadata


class TestRAGAgent:
    @pytest.mark.asyncio
    async def test_generate_answer_with_chunks(self):
        """Test answer generation with retrieved chunks."""
        agent = RAGAgent()

        # Mock the retrieval service
        with patch('src.agents.rag_agent.retrieve_chunks') as mock_retrieve:
            mock_chunk = RetrievedChunk(
                chunk_id="test_chunk_1",
                content="This is test content from the textbook.",
                metadata=ChunkMetadata(
                    chapter="Chapter 1",
                    section="Section 1.1",
                    source_document="test_doc"
                ),
                score=0.9
            )
            mock_retrieve.return_value = ([mock_chunk], 10.0)  # chunks, retrieval_time

            # Mock the OpenAI client
            with patch.object(agent, 'client') as mock_client:
                mock_response = AsyncMock()
                mock_response.choices = [AsyncMock()]
                mock_response.choices[0].message.content = "This is the generated answer based on the context."
                mock_response.usage = AsyncMock()
                mock_response.usage.prompt_tokens = 100
                mock_response.usage.completion_tokens = 50
                mock_response.usage.total_tokens = 150
                mock_client.chat.completions.create.return_value = mock_response

                answer, citations, reasoning, token_usage = await agent.generate_answer("test query", top_k=1)

                assert answer == "This is the generated answer based on the context."
                assert len(citations) == 1
                assert citations[0].chunk_id == "test_chunk_1"
                assert token_usage.total_tokens == 150

    @pytest.mark.asyncio
    async def test_generate_answer_no_chunks(self):
        """Test answer generation when no chunks are retrieved."""
        agent = RAGAgent()

        # Mock the retrieval service to return no chunks
        with patch('src.agents.rag_agent.retrieve_chunks') as mock_retrieve:
            mock_retrieve.return_value = ([], 5.0)  # empty chunks list

            answer, citations, reasoning, token_usage = await agent.generate_answer("test query", top_k=1)

            assert answer == "I cannot find relevant information in the book to answer this question."
            assert len(citations) == 0
            assert len(reasoning) > 0  # Should have some reasoning
            assert token_usage.total_tokens == 0