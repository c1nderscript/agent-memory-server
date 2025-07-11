import os
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from agent_memory_server.llms import (
    ModelProvider,
    OpenAIClientWrapper,
    get_model_client,
    get_model_config,
)


@pytest.mark.asyncio
class TestOpenAIClientWrapper:
    @patch.dict(
        os.environ,
        {
            "OPENAI_API_KEY": "test-key",
        },
    )
    @patch("agent_memory_server.llms.AsyncOpenAI")
    async def test_init_regular_openai(self, mock_openai):
        """Test initializing with regular OpenAI"""
        # Set up the mock to return an AsyncMock
        mock_openai.return_value = AsyncMock()

        OpenAIClientWrapper()

        # Verify the client was created
        assert mock_openai.called

    @patch.object(OpenAIClientWrapper, "__init__", return_value=None)
    async def test_create_embedding(self, mock_init):
        """Test creating embeddings"""
        # Create a client with mocked init
        client = OpenAIClientWrapper()

        # Mock the embedding client and response
        mock_response = AsyncMock()
        mock_response.data = [
            MagicMock(embedding=[0.1, 0.2, 0.3]),
            MagicMock(embedding=[0.4, 0.5, 0.6]),
        ]

        client.embedding_client = AsyncMock()
        client.embedding_client.embeddings.create = AsyncMock(
            return_value=mock_response
        )

        # Test creating embeddings
        query_vec = ["Hello, world!", "How are you?"]
        embeddings = await client.create_embedding(query_vec)

        # Verify embeddings were created correctly
        assert len(embeddings) == 2
        # Convert NumPy array to list or use np.array_equal for comparison
        assert np.array_equal(
            embeddings[0], np.array([0.1, 0.2, 0.3], dtype=np.float32)
        )
        assert np.array_equal(
            embeddings[1], np.array([0.4, 0.5, 0.6], dtype=np.float32)
        )

        # Verify the client was called with correct parameters
        client.embedding_client.embeddings.create.assert_called_with(
            model="text-embedding-ada-002", input=query_vec
        )

    @patch.object(OpenAIClientWrapper, "__init__", return_value=None)
    async def test_create_chat_completion(self, mock_init):
        """Test creating chat completions"""
        # Create a client with mocked init
        client = OpenAIClientWrapper()

        # Mock the completion client and response
        # Create a response structure that matches our new ChatResponse format
        mock_response = AsyncMock()
        mock_response.choices = [{"message": {"content": "Test response"}}]
        mock_response.usage = {"total_tokens": 100}

        client.completion_client = AsyncMock()
        client.completion_client.chat.completions.create = AsyncMock(
            return_value=mock_response
        )

        # Test creating chat completion
        model = "gpt-3.5-turbo"
        prompt = "Hello, world!"
        response = await client.create_chat_completion(model, prompt)

        # Verify the response contains the expected structure
        assert response.choices[0]["message"]["content"] == "Test response"
        assert response.total_tokens == 100

        # Verify the client was called with correct parameters
        client.completion_client.chat.completions.create.assert_called_with(
            model=model, messages=[{"role": "user", "content": prompt}]
        )


@pytest.mark.parametrize(
    ("model_name", "expected_provider", "expected_max_tokens"),
    [
        ("gpt-4o", "openai", 128000),
        ("claude-3-sonnet-20240229", "anthropic", 200000),
        ("nonexistent-model", "openai", 128000),  # Should default to GPT-4o-mini
    ],
)
def test_get_model_config(model_name, expected_provider, expected_max_tokens):
    """Test the get_model_config function"""
    # Get the model config
    config = get_model_config(model_name)

    # Check the provider
    if expected_provider == "openai":
        assert config.provider == ModelProvider.OPENAI
    else:
        assert config.provider == ModelProvider.ANTHROPIC

    # Check the max tokens
    assert config.max_tokens == expected_max_tokens


@pytest.mark.asyncio
async def test_get_model_client():
    """Test the get_model_client function and caching by provider"""
    # Test with OpenAI provider
    with (
        patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}),
        patch("agent_memory_server.llms.OpenAIClientWrapper") as mock_openai,
    ):
        mock_openai.return_value = "openai-client"
        client1 = await get_model_client(ModelProvider.OPENAI)
        client2 = await get_model_client(ModelProvider.OPENAI)
        assert client1 == "openai-client"
        assert client1 is client2
        mock_openai.assert_called_once()

    # Test with Anthropic provider
    with (
        patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}),
        patch("agent_memory_server.llms.AnthropicClientWrapper") as mock_anthropic,
    ):
        mock_anthropic.return_value = "anthropic-client"
        client1 = await get_model_client(ModelProvider.ANTHROPIC)
        client2 = await get_model_client(ModelProvider.ANTHROPIC)
        assert client1 == "anthropic-client"
        assert client1 is client2
        mock_anthropic.assert_called_once()
