import sys
import types
from unittest.mock import patch

import pytest


# Provide minimal stubs for optional dependencies used during module import
if "transformers" not in sys.modules:
    transformers_stub = types.ModuleType("transformers")
    transformers_stub.AutoModelForTokenClassification = object
    transformers_stub.AutoTokenizer = object
    transformers_stub.pipeline = lambda *args, **kwargs: None
    sys.modules["transformers"] = transformers_stub

if "redisvl" not in sys.modules:
    redisvl = types.ModuleType("redisvl")
    query = types.ModuleType("redisvl.query")
    filter_mod = types.ModuleType("redisvl.query.filter")
    filter_mod.FilterExpression = object
    filter_mod.Num = object
    filter_mod.Tag = object
    query.filter = filter_mod
    redisvl.query = query
    sys.modules["redisvl"] = redisvl
    sys.modules["redisvl.query"] = query
    sys.modules["redisvl.query.filter"] = filter_mod

if "openai" not in sys.modules:
    sys.modules["openai"] = types.ModuleType("openai")
if "anthropic" not in sys.modules:
    sys.modules["anthropic"] = types.ModuleType("anthropic")

from unittest.mock import Mock

import numpy as np

from agent_memory_server.extraction import _bertopic_cache, extract_topics_bertopic


@pytest.fixture(autouse=True)
def clear_cache():
    _bertopic_cache.clear()
    yield
    _bertopic_cache.clear()


@pytest.fixture
def mock_bertopic():
    mock = Mock()
    mock.transform.return_value = (np.array([1]), np.array([0.8]))
    mock.get_topic.side_effect = lambda x: [("technology", 0.8)]
    return mock


class TestTopicCaching:
    @patch("agent_memory_server.extraction.get_topic_model")
    def test_cached_result_returned(self, mock_get_topic_model, mock_bertopic):
        mock_get_topic_model.return_value = mock_bertopic
        text = "Testing caching"
        topics_first = extract_topics_bertopic(text, num_topics=2)
        topics_second = extract_topics_bertopic(text, num_topics=2)
        assert topics_first == topics_second
        mock_bertopic.transform.assert_called_once_with([text])

    @patch("agent_memory_server.extraction.get_topic_model")
    def test_cache_key_includes_num_topics(self, mock_get_topic_model, mock_bertopic):
        mock_get_topic_model.return_value = mock_bertopic
        text = "Testing caching"
        _ = extract_topics_bertopic(text, num_topics=2)
        _ = extract_topics_bertopic(text, num_topics=3)
        assert mock_bertopic.transform.call_count == 2
