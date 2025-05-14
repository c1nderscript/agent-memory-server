from time import time
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import nanoid
import numpy as np
import pytest
from redis.commands.search.document import Document

from agent_memory_server.filters import SessionId
from agent_memory_server.long_term_memory import (
    index_long_term_memories,
    search_long_term_memories,
)
from agent_memory_server.models import LongTermMemory, LongTermMemoryResult
from agent_memory_server.utils.redis import ensure_search_index_exists


class TestLongTermMemory:
    @pytest.mark.asyncio
    async def test_index_memories(
        self, mock_openai_client, mock_async_redis_client, session
    ):
        """Test indexing messages"""
        long_term_memories = [
            LongTermMemory(text="Paris is the capital of France", session_id=session),
            LongTermMemory(text="France is a country in Europe", session_id=session),
        ]

        # Create two separate embedding vectors
        mock_vectors = [
            np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32).tobytes(),
            np.array([0.5, 0.6, 0.7, 0.8], dtype=np.float32).tobytes(),
        ]

        mock_vectorizer = MagicMock()
        mock_vectorizer.aembed_many = AsyncMock(return_value=mock_vectors)

        mock_async_redis_client.hset = AsyncMock()

        with mock.patch(
            "agent_memory_server.long_term_memory.OpenAITextVectorizer",
            return_value=mock_vectorizer,
        ):
            await index_long_term_memories(
                long_term_memories,
                redis_client=mock_async_redis_client,
            )

        # Check that create_embedding was called with the right arguments
        contents = [memory.text for memory in long_term_memories]
        mock_vectorizer.aembed_many.assert_called_with(
            contents,
            batch_size=20,
            as_buffer=True,
        )

        # Verify one of the calls to make sure the data is correct
        for i, call in enumerate(mock_async_redis_client.hset.call_args_list):
            args, kwargs = call

            # Check that the key starts with the memory key prefix
            assert args[0].startswith("memory:")

            # Check that the mapping contains the right keys
            mapping = kwargs["mapping"]
            assert mapping == {
                "text": long_term_memories[i].text,
                "id_": long_term_memories[i].id_,
                "session_id": long_term_memories[i].session_id,
                "user_id": long_term_memories[i].user_id,
                "last_accessed": long_term_memories[i].last_accessed,
                "created_at": long_term_memories[i].created_at,
                "vector": mock_vectors[i],
            }

    @pytest.mark.asyncio
    async def test_search_memories(self, mock_openai_client, mock_async_redis_client):
        """Test searching memories"""
        # Set up the mock embedding response
        mock_vector = np.array([0.1, 0.2, 0.3, 0.4], dtype=np.float32)
        mock_vectorizer = MagicMock()
        mock_vectorizer.aembed = AsyncMock(return_value=mock_vector)

        class MockResult:
            def __init__(self, docs):
                self.total = len(docs)
                self.docs = docs

        mock_now = time()

        mock_query = AsyncMock()
        # Return a list of documents directly instead of a MockResult object
        mock_query.return_value = [
            Document(
                id=b"doc1",
                id_=nanoid.generate(),
                text=b"Hello, world!",
                vector_distance=0.25,
                created_at=mock_now,
                last_accessed=mock_now,
                user_id=None,
                session_id=None,
                namespace=None,
                topics=None,
                entities=None,
            ),
            Document(
                id=b"doc2",
                id_=nanoid.generate(),
                text=b"Hi there!",
                vector_distance=0.75,
                created_at=mock_now,
                last_accessed=mock_now,
                user_id=None,
                session_id=None,
                namespace=None,
                topics=None,
                entities=None,
            ),
        ]

        mock_index = MagicMock()
        mock_index.query = mock_query

        query = "What is the meaning of life?"
        session_id = SessionId(eq="test-session")

        with (
            mock.patch(
                "agent_memory_server.long_term_memory.OpenAITextVectorizer",
                return_value=mock_vectorizer,
            ),
            mock.patch(
                "agent_memory_server.long_term_memory.get_search_index",
                return_value=mock_index,
            ),
        ):
            results = await search_long_term_memories(
                query,
                mock_async_redis_client,
                session_id=session_id,
            )

        # Check that create_embedding was called with the right arguments
        mock_vectorizer.aembed.assert_called_with(query)

        assert mock_index.query.call_count == 1

        assert len(results.memories) == 2
        assert isinstance(results.memories[0], LongTermMemoryResult)
        assert results.memories[0].text == "Hello, world!"
        assert results.memories[0].dist == 0.25
        assert results.memories[1].text == "Hi there!"
        assert results.memories[1].dist == 0.75


@pytest.mark.requires_api_keys
class TestLongTermMemoryIntegration:
    """Integration tests for long-term memory"""

    @pytest.mark.asyncio
    async def test_search_messages(self, async_redis_client):
        """Test searching messages"""
        await ensure_search_index_exists(async_redis_client)

        long_term_memories = [
            LongTermMemory(text="Paris is the capital of France", session_id="123"),
            LongTermMemory(text="France is a country in Europe", session_id="123"),
        ]

        with mock.patch(
            "agent_memory_server.long_term_memory.get_redis_conn",
            return_value=async_redis_client,
        ):
            await index_long_term_memories(
                long_term_memories,
                redis_client=async_redis_client,
            )

        results = await search_long_term_memories(
            "What is the capital of France?",
            async_redis_client,
            session_id=SessionId(eq="123"),
            limit=1,
        )

        assert results.total == 1
        assert len(results.memories) == 1
        assert results.memories[0].text == "Paris is the capital of France"
        assert results.memories[0].session_id == "123"

    @pytest.mark.asyncio
    async def test_search_messages_with_distance_threshold(self, async_redis_client):
        """Test searching messages with a distance threshold"""
        await ensure_search_index_exists(async_redis_client)

        long_term_memories = [
            LongTermMemory(text="Paris is the capital of France", session_id="123"),
            LongTermMemory(text="France is a country in Europe", session_id="123"),
        ]

        with mock.patch(
            "agent_memory_server.long_term_memory.get_redis_conn",
            return_value=async_redis_client,
        ):
            await index_long_term_memories(
                long_term_memories,
                redis_client=async_redis_client,
            )

        results = await search_long_term_memories(
            "What is the capital of France?",
            async_redis_client,
            session_id=SessionId(eq="123"),
            distance_threshold=0.1,
            limit=2,
        )

        assert results.total == 1
        assert len(results.memories) == 1
        assert results.memories[0].text == "Paris is the capital of France"
        assert results.memories[0].session_id == "123"
