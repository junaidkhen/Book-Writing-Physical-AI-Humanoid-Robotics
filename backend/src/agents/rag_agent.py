from typing import List, Dict, Any, Tuple, AsyncGenerator
from openai import AsyncOpenAI
from ..services.retrieval_service import retrieve_chunks
from ..schemas.response_schemas import RetrievedChunk, Citation, TokenUsage, ResponseMetadata
from ..config.settings import settings
from ..utils.logging import logger
import time
import json
import httpx


class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) Agent that retrieves information from
    Qdrant and uses Gemini 2.5 Flash or OpenAI to generate grounded answers.
    """

    def __init__(self):
        # Create async httpx client
        http_client = httpx.AsyncClient(timeout=60.0)

        # Determine which API to use (prefer Gemini, fallback to OpenAI)
        if settings.gemini_api_key:
            # Use Gemini API via OpenAI-compatible endpoint
            self.client = AsyncOpenAI(
                api_key=settings.gemini_api_key,
                base_url=settings.gemini_base_url,
                http_client=http_client
            )
            self.model = settings.gemini_model
            self.api_type = "gemini"
            logger.info("Initialized RAG Agent with Gemini 2.5 Flash")
        elif settings.openai_api_key:
            # Fallback to OpenAI
            self.client = AsyncOpenAI(
                api_key=settings.openai_api_key,
                http_client=http_client
            )
            self.model = settings.openai_model
            self.api_type = "openai"
            logger.info("Initialized RAG Agent with OpenAI (Gemini key not found)")
        else:
            raise ValueError(
                "No API key found! Please set either GEMINI_API_KEY or OPENAI_API_KEY in your .env file"
            )

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
            answer = "I couldn't find specific information about this topic in the textbook. This might be because: (1) the topic isn't covered in the available chapters, (2) it's discussed using different terminology, or (3) the search didn't match the content closely enough. Try rephrasing your question or using different keywords."
            citations = []
            reasoning = ["Query interpretation: User asked a question",
                        "Retrieval results: No relevant chunks found in the book (after filtering duplicates and UI text)",
                        "Synthesis logic: Cannot generate answer without relevant context"]
            token_usage = TokenUsage(input_tokens=0, output_tokens=0, total_tokens=0)
            return answer, citations, reasoning, token_usage

        # Step 2: Format the context from retrieved chunks
        context_str = "\n\n".join([
            f"Document ID: {chunk.chunk_id}\nContent: {chunk.content}\nSource: Chapter {chunk.metadata.chapter}, Section {chunk.metadata.section}"
            for chunk in retrieved_chunks
        ])

        # Step 3: Create the prompt for the Gemini agent
        system_prompt = f"""You are an expert assistant for the Physical AI & Humanoid Robotics textbook.
Your task is to answer questions based ONLY on the provided context from the textbook.
Do not use any external knowledge or make up information.

Answer the user's question using the information provided in the context below.

Important guidelines:
- Use ALL relevant information from the context to provide a comprehensive answer
- If the context contains partial information, answer what you can and mention what's missing
- If the context contains related but not exact information, explain the connection
- Only say "I cannot find relevant information" if the context is completely unrelated
- Provide detailed explanations with examples when available
- Use plain text format (no markdown unless explicitly requested)

Context from textbook:
{context_str}
"""

        user_prompt = f"Question: {query}\n\nProvide a clear, concise answer based only on the context above."

        try:
            # Step 4: Call the Gemini API via OpenAI-compatible endpoint
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract the response (plain text from Gemini)
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

            # Create reasoning steps
            model_name = "Gemini 2.5 Flash" if self.api_type == "gemini" else f"OpenAI {self.model}"
            reasoning = [
                f"Query interpretation: Answering '{query[:50]}...'",
                f"Retrieval results: Found {len(retrieved_chunks)} relevant chunks from the textbook",
                f"Synthesis logic: Generated answer using {model_name} based on retrieved context"
            ]

            # Calculate token usage
            token_usage = TokenUsage(
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                total_tokens=response.usage.total_tokens if response.usage else 0
            )

            agent_time = (time.time() - start_time - retrieval_time/1000) * 1000  # Convert to milliseconds
            logger.info(f"{self.api_type.upper()} agent processed query in {agent_time:.2f}ms, tokens used: {token_usage.total_tokens}")

            return answer, citations, reasoning, token_usage

        except Exception as e:
            logger.error(f"Error in RAG agent with {self.api_type.upper()}: {str(e)}")
            # Check for common API errors and provide user-friendly messages
            error_str = str(e).lower()
            api_name = "Gemini" if self.api_type == "gemini" else "OpenAI"

            if "quota" in error_str or "rate" in error_str:
                raise Exception(f"{api_name} API quota exceeded or rate limit reached. Please wait and try again.")
            elif "authentication" in error_str or "invalid" in error_str or "api_key" in error_str:
                api_key_name = "GEMINI_API_KEY" if self.api_type == "gemini" else "OPENAI_API_KEY"
                raise Exception(f"Invalid {api_name} API key. Please check your {api_key_name} configuration.")
            elif "not found" in error_str or "model" in error_str:
                raise Exception(f"Model {self.model} not available. Please verify the model name in your configuration.")
            else:
                raise Exception(f"Error communicating with {api_name} API: {str(e)}")

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

    async def query_stream(self, query: str, context: str = None, top_k: int = 5) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream the response to a query in real-time.

        Args:
            query: The user's question
            context: Optional additional context
            top_k: Number of chunks to retrieve

        Yields:
            Dict chunks in the format:
                - {"type": "content", "data": {"text": "..."}}
                - {"type": "citation", "data": {...}}
                - {"type": "done", "data": {}}
        """
        try:
            # Step 1: Retrieve relevant chunks
            retrieved_chunks, retrieval_time = await retrieve_chunks(query, top_k)
            logger.info(f"Retrieved {len(retrieved_chunks)} chunks for streaming query: {query[:50]}...")

            if not retrieved_chunks:
                # If no relevant chunks found, return appropriate response
                yield {"type": "content", "data": {"text": "I couldn't find specific information about this topic in the textbook. This might be because: (1) the topic isn't covered in the available chapters, (2) it's discussed using different terminology, or (3) the search didn't match the content closely enough. Try rephrasing your question or using different keywords."}}
                yield {"type": "done", "data": {}}
                return

            # Step 2: Format the context from retrieved chunks
            context_str = "\n\n".join([
                f"Document ID: {chunk.chunk_id}\nContent: {chunk.content}\nSource: Chapter {chunk.metadata.chapter}, Section {chunk.metadata.section}"
                for chunk in retrieved_chunks
            ])

            # Combine with additional context if provided
            full_context = context_str
            if context:
                full_context = f"{context}\n\n{context_str}"

            # Step 3: Create the prompt for the Gemini agent
            system_prompt = f"""You are an expert assistant for the Physical AI & Humanoid Robotics textbook.
Your task is to answer questions based ONLY on the provided context from the textbook.
Do not use any external knowledge or make up information.

Answer the user's question using the information provided in the context below.

Important guidelines:
- Use ALL relevant information from the context to provide a comprehensive answer
- If the context contains partial information, answer what you can and mention what's missing
- If the context contains related but not exact information, explain the connection
- Only say "I cannot find relevant information" if the context is completely unrelated
- Provide detailed explanations with examples when available
- Use plain text format (no markdown unless requested)

Context: {full_context}"""

            user_prompt = f"Question: {query}\n\nProvide a clear, concise answer based only on the context above."

            # Step 4: Call the Gemini API with streaming enabled
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )

            # Step 5: Stream the response chunks
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield {"type": "content", "data": {"text": content}}

            # Step 6: Send citations after the main content
            for chunk in retrieved_chunks:
                citation_data = {
                    "id": chunk.chunk_id,
                    "title": f"Chapter {chunk.metadata.chapter}: {chunk.metadata.section}",
                    "url": f"/docs/chapter-{chunk.metadata.chapter}",
                    "text": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                    "page": chunk.metadata.page,
                    "chapter": chunk.metadata.chapter,
                    "score": float(chunk.score)
                }
                yield {"type": "citation", "data": citation_data}

            # Step 7: Send done signal
            yield {"type": "done", "data": {}}

            logger.info(f"Completed streaming response for query: {query[:50]}...")

        except Exception as e:
            logger.error(f"Error in streaming RAG agent with {self.api_type.upper()}: {str(e)}")
            error_str = str(e).lower()
            api_name = "Gemini" if self.api_type == "gemini" else "OpenAI"
            api_key_name = "GEMINI_API_KEY" if self.api_type == "gemini" else "OPENAI_API_KEY"

            # Check for common API errors and provide user-friendly messages
            if "quota" in error_str or "rate" in error_str:
                yield {"type": "error", "data": {"message": f"{api_name} API quota exceeded or rate limit reached. Please wait and try again."}}
            elif "authentication" in error_str or "invalid" in error_str or "api_key" in error_str:
                yield {"type": "error", "data": {"message": f"Invalid {api_name} API key. Please check your {api_key_name} configuration."}}
            elif "not found" in error_str or "model" in error_str:
                yield {"type": "error", "data": {"message": f"Model {self.model} not available. Please verify the model name."}}
            else:
                yield {"type": "error", "data": {"message": f"Error processing query with {api_name}: {str(e)}"}}
            yield {"type": "done", "data": {}}


# Global instance of the RAG agent
rag_agent = RAGAgent()