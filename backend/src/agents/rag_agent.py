from typing import List, Dict, Any, Tuple
from openai import OpenAI
from ..clients.openai_client import openai_client
from ..services.retrieval_service import retrieve_chunks
from ..schemas.response_schemas import RetrievedChunk, Citation, TokenUsage, ResponseMetadata
from ..config.settings import settings
from ..utils.logging import logger
import time
import json


class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) Agent that retrieves information from
    Qdrant and uses OpenAI to generate grounded answers.
    """

    def __init__(self):
        self.client = openai_client
        self.model = settings.openai_model
        self.temperature = settings.temperature
        self.max_tokens = settings.max_tokens

    async def generate_answer(
        self,
        query: str,
        top_k: int = 5
    ) -> Tuple[str, List[Citation], List[str], TokenUsage]:
        """
        Generate an answer to the query using retrieved context.

        Args:
            query: The user's question
            top_k: Number of chunks to retrieve

        Returns:
            Tuple of (answer, citations, reasoning, token_usage)
        """
        start_time = time.time()

        # Step 1: Retrieve relevant chunks
        retrieved_chunks, retrieval_time = await retrieve_chunks(query, top_k)
        logger.info(f"Retrieved {len(retrieved_chunks)} chunks for query: {query[:50]}...")

        if not retrieved_chunks:
            # If no relevant chunks found, return appropriate response
            answer = "I cannot find relevant information in the book to answer this question."
            citations = []
            reasoning = ["Query interpretation: User asked a question",
                        "Retrieval results: No relevant chunks found in the book",
                        "Synthesis logic: Cannot generate answer without relevant context"]
            token_usage = TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0)
            return answer, citations, reasoning, token_usage

        # Step 2: Format the context from retrieved chunks
        context_str = "\n\n".join([
            f"Document ID: {chunk.chunk_id}\nContent: {chunk.content}\nSource: Chapter {chunk.metadata.chapter}, Section {chunk.metadata.section}"
            for chunk in retrieved_chunks
        ])

        # Step 3: Create the prompt for the OpenAI agent
        system_prompt = f"""
        You are an expert assistant for the Physical AI & Humanoid Robotics textbook.
        Your task is to answer questions based ONLY on the provided context from the textbook.
        Do not use any external knowledge or make up information.

        Answer the user's question using only the information provided in the context.
        If the context doesn't contain enough information to answer the question, say so explicitly.

        Your response should include:
        1. A clear answer to the question
        2. Citations to specific parts of the context that support your answer
        3. Brief reasoning steps explaining how you arrived at the answer

        Context: {context_str}
        """

        user_prompt = f"Question: {query}\n\nPlease provide a detailed answer based only on the context provided above."

        try:
            # Step 4: Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}  # Request JSON response
            )

            # Extract the response
            response_text = response.choices[0].message.content
            response_data = json.loads(response_text)

            # Parse the response - this might need adjustment based on the actual response format
            # For now, assuming the response is structured as requested
            answer = response_data.get("answer", response_text) if isinstance(response_data, dict) else response_text
            reasoning = response_data.get("reasoning", ["Processing completed"]) if isinstance(response_data, dict) else ["Processing completed"]

            # Create citations from the retrieved chunks
            citations = []
            for chunk in retrieved_chunks:
                citation = Citation(
                    chunk_id=chunk.chunk_id,
                    chapter=chunk.metadata.chapter,
                    section=chunk.metadata.section,
                    page=chunk.metadata.page,
                    score=chunk.score
                )
                citations.append(citation)

            # Calculate token usage
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0
            )

            agent_time = (time.time() - start_time - retrieval_time/1000) * 1000  # Convert to milliseconds
            logger.info(f"Agent processed query in {agent_time:.2f}ms, tokens used: {token_usage.total_tokens}")

            return answer, citations, reasoning, token_usage

        except json.JSONDecodeError:
            # If JSON parsing fails, return a plain text response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"You are an expert assistant for the Physical AI & Humanoid Robotics textbook. Answer the user's question based ONLY on the provided context: {context_str}"},
                    {"role": "user", "content": query}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            answer = response.choices[0].message.content

            # Create citations from the retrieved chunks
            citations = []
            for chunk in retrieved_chunks:
                citation = Citation(
                    chunk_id=chunk.chunk_id,
                    chapter=chunk.metadata.chapter,
                    section=chunk.metadata.section,
                    page=chunk.metadata.page,
                    score=chunk.score
                )
                citations.append(citation)

            # Create basic reasoning
            reasoning = [
                f"Query interpretation: Answering '{query}'",
                f"Retrieval results: Found {len(retrieved_chunks)} relevant chunks",
                "Synthesis logic: Generated answer based on retrieved context"
            ]

            # Calculate token usage
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0
            )

            agent_time = (time.time() - start_time - retrieval_time/1000) * 1000  # Convert to milliseconds
            logger.info(f"Agent processed query in {agent_time:.2f}ms, tokens used: {token_usage.total_tokens}")

            return answer, citations, reasoning, token_usage

        except Exception as e:
            logger.error(f"Error in RAG agent: {str(e)}")
            raise e

    async def query(self, query: str, top_k: int = 5, temperature: float = 0.1) -> Tuple[str, List[Citation], List[str], ResponseMetadata]:
        """
        Main query method that orchestrates the RAG process.
        """
        original_temperature = self.temperature
        try:
            # Temporarily set the temperature if provided
            if temperature is not None:
                self.temperature = temperature

            start_time = time.time()

            # Generate the answer
            answer, citations, reasoning, token_usage = await self.generate_answer(query, top_k)

            total_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            # We'll estimate retrieval and agent times - in a real implementation these would be more precise
            retrieval_time = min(total_time * 0.3, 1000)  # Estimate: 30% of total time or max 1s
            agent_time = total_time - retrieval_time

            metadata = ResponseMetadata(
                token_usage=token_usage,
                retrieval_time=retrieval_time,
                agent_time=agent_time,
                total_time=total_time,
                chunks_retrieved=len(citations)  # Using citations count as proxy for chunks
            )

            return answer, citations, reasoning, metadata

        finally:
            # Restore original temperature
            self.temperature = original_temperature


# Global instance of the RAG agent
rag_agent = RAGAgent()