import json
import os
import hashlib
from typing import TYPE_CHECKING, Any

import ulid
from tenacity.asyncio import AsyncRetrying
from tenacity.stop import stop_after_attempt
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

from agent_memory_server.config import settings
from agent_memory_server.filters import DiscreteMemoryExtracted, MemoryType
from agent_memory_server.llms import (
    AnthropicClientWrapper,
    OpenAIClientWrapper,
    get_model_client,
    get_model_config,
)
from agent_memory_server.logging import get_logger
from agent_memory_server.models import MemoryRecord


if TYPE_CHECKING:
    from bertopic import BERTopic


logger = get_logger(__name__)

# Set tokenizer parallelism environment variable
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Global model instances
_topic_model: "BERTopic | None" = None
_ner_model: Any | None = None
_ner_tokenizer: Any | None = None
_entity_cache: dict[str, list[str]] = {}


def _entity_cache_key(text: str) -> str:
    """Return a stable cache key for the given text."""
    return hashlib.md5(text.encode()).hexdigest()

# Cache for BERTopic topic extraction results
_bertopic_cache: dict[tuple[str, int], list[str]] = {}


def get_topic_model() -> "BERTopic":
    """
    Get or initialize the BERTopic model.

    Returns:
        The BERTopic model instance
    """
    from bertopic import BERTopic

    global _topic_model
    if _topic_model is None:
        _topic_model = BERTopic.load(
            settings.topic_model_path, embedding_model="all-MiniLM-L6-v2"
        )
    return _topic_model  # type: ignore


def get_ner_model() -> Any:
    """
    Get or initialize the NER model and tokenizer.

    Returns:
        The NER pipeline instance
    """
    global _ner_model, _ner_tokenizer
    if _ner_model is None:
        _ner_tokenizer = AutoTokenizer.from_pretrained(settings.ner_model)
        _ner_model = AutoModelForTokenClassification.from_pretrained(settings.ner_model)
    return pipeline("ner", model=_ner_model, tokenizer=_ner_tokenizer)


def extract_entities(text: str) -> list[str]:
    """
    Extract named entities from text using the NER model.

    Results are cached in memory using a key derived from the input text.

    Args:
        text: The text to extract entities from

    Returns:
        List of unique entity names
    """
    cache_key = _entity_cache_key(text)
    if cached := _entity_cache.get(cache_key):
        return cached

    try:
        ner = get_ner_model()
        results = ner(text)

        # Group tokens by entity
        current_entity = []
        entities = []

        for result in results:
            if result["word"].startswith("##"):
                # This is a continuation of the previous entity
                current_entity.append(result["word"][2:])
            else:
                # This is a new entity
                if current_entity:
                    entities.append("".join(current_entity))
                current_entity = [result["word"]]

        # Add the last entity if exists
        if current_entity:
            entities.append("".join(current_entity))

        deduped = list(set(entities))
        _entity_cache[cache_key] = deduped
        return deduped

    except Exception as e:
        logger.error(f"Error extracting entities: {e}")
        return []


async def extract_topics_llm(
    text: str,
    num_topics: int | None = None,
    client: OpenAIClientWrapper | AnthropicClientWrapper | None = None,
) -> list[str]:
    """
    Extract topics from text using the LLM model.
    """
    if client:
        _client = client
    else:
        provider = get_model_config(settings.topic_model).provider
        _client = await get_model_client(provider)
    _num_topics = num_topics if num_topics is not None else settings.top_k_topics

    prompt = f"""
    Extract the topic {_num_topics} topics from the following text:
    {text}

    Return a list of topics in JSON format, for example:
    {{
        "topics": ["topic1", "topic2", "topic3"]
    }}
    """
    topics = []

    async for attempt in AsyncRetrying(stop=stop_after_attempt(3)):
        with attempt:
            response = await _client.create_chat_completion(
                model=settings.generation_model,
                prompt=prompt,
                response_format={"type": "json_object"},
            )
            try:
                topics = json.loads(response.choices[0].message.content)["topics"]
            except (json.JSONDecodeError, KeyError):
                logger.error(
                    f"Error decoding JSON: {response.choices[0].message.content}"
                )
                topics = []
            if topics:
                topics = topics[:_num_topics]

    return topics


def extract_topics_bertopic(text: str, num_topics: int | None = None) -> list[str]:
    """
    Extract topics from text using the BERTopic model.

    Args:
        text: The text to extract topics from
        num_topics: Number of topics to return. Defaults to settings.top_k_topics

    Returns:
        List of topic labels
    """
    _num_topics = num_topics if num_topics is not None else settings.top_k_topics
    cache_key = (text, _num_topics)
    if cache_key in _bertopic_cache:
        return _bertopic_cache[cache_key]

    model = get_topic_model()
    topic_indices, _ = model.transform([text])
    topics: list[str] = []

    for i, topic_idx in enumerate(topic_indices):
        if _num_topics and i >= _num_topics:
            break
        topic_idx_int = int(topic_idx)
        if topic_idx_int != -1:  # Skip outlier topic (-1)
            topic_info: list[tuple[str, float]] = model.get_topic(topic_idx_int)  # type: ignore
            if topic_info:
                topics.extend([info[0] for info in topic_info])

    _bertopic_cache[cache_key] = topics
    return topics


async def handle_extraction(text: str) -> tuple[list[str], list[str]]:
    """
    Handle topic and entity extraction for a message.

    Args:
        text: The text to process

    Returns:
        Tuple of extracted topics and entities
    """
    # Extract topics if enabled
    topics = []
    if settings.enable_topic_extraction:
        if settings.topic_model_source == "BERTopic":
            topics = extract_topics_bertopic(text)
        else:
            topics = await extract_topics_llm(text)

    # Extract entities if enabled
    entities = []
    if settings.enable_ner:
        entities = extract_entities(text)

    # Merge with existing topics and entities
    if topics:
        topics = list(set(topics))
    if entities:
        entities = list(set(entities))

    return topics, entities


DISCRETE_EXTRACTION_PROMPT = """
    You are a long-memory manager. Your job is to analyze text and extract
    information that might be useful in future conversations with users.

    Extract two types of memories:
    1. EPISODIC: Personal experiences specific to a user or agent.
       Example: "User prefers window seats" or "User had a bad experience in Paris"

    2. SEMANTIC: User preferences and general knowledge outside of your training data.
       Example: "Trek discontinued the Trek 520 steel touring bike in 2023"

    For each memory, return a JSON object with the following fields:
    - type: str --The memory type, either "episodic" or "semantic"
    - text: str -- The actual information to store
    - topics: list[str] -- The topics of the memory (top {top_k_topics})
    - entities: list[str] -- The entities of the memory
    -

    Return a list of memories, for example:
    {{
        "memories": [
            {{
                "type": "semantic",
                "text": "User prefers window seats",
                "topics": ["travel", "airline"],
                "entities": ["User", "window seat"],
            }},
            {{
                "type": "episodic",
                "text": "Trek discontinued the Trek 520 steel touring bike in 2023",
                "topics": ["travel", "bicycle"],
                "entities": ["Trek", "Trek 520 steel touring bike"],
            }},
        ]
    }}

    IMPORTANT RULES:
    1. Only extract information that would be genuinely useful for future interactions.
    2. Do not extract procedural knowledge - that is handled by the system's built-in tools and prompts.
    3. You are a large language model - do not extract facts that you already know.

    Message:
    {message}

    Extracted memories:
    """


async def extract_discrete_memories(
    memories: list[MemoryRecord] | None = None,
    deduplicate: bool = True,
):
    """
    Extract episodic and semantic memories from text using an LLM.
    """
    provider = get_model_config(settings.generation_model).provider
    client = await get_model_client(provider)

    # Use vectorstore adapter to find messages that need discrete memory extraction
    # TODO: Sort out circular imports
    from agent_memory_server.long_term_memory import index_long_term_memories
    from agent_memory_server.vectorstore_factory import get_vectorstore_adapter

    adapter = await get_vectorstore_adapter()

    if not memories:
        # If no memories are provided, search for any messages in long-term memory
        # that haven't been processed for discrete extraction

        memories = []
        offset = 0
        while True:
            search_result = await adapter.search_memories(
                query="",  # Empty query to get all messages
                memory_type=MemoryType(eq="message"),
                discrete_memory_extracted=DiscreteMemoryExtracted(eq="f"),
                limit=25,
                offset=offset,
            )

            logger.info(
                f"Found {len(search_result.memories)} memories to extract: {[m.id for m in search_result.memories]}"
            )

            memories += search_result.memories

            if len(search_result.memories) < 25:
                break

            offset += 25

    new_discrete_memories = []
    updated_memories = []

    for memory in memories:
        if not memory or not memory.text:
            logger.info(f"Deleting memory with no text: {memory}")
            await adapter.delete_memories([memory.id])
            continue

        async for attempt in AsyncRetrying(stop=stop_after_attempt(3)):
            with attempt:
                response = await client.create_chat_completion(
                    model=settings.generation_model,
                    prompt=DISCRETE_EXTRACTION_PROMPT.format(
                        message=memory.text, top_k_topics=settings.top_k_topics
                    ),
                    response_format={"type": "json_object"},
                )
                try:
                    new_message = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    logger.error(
                        f"Error decoding JSON: {response.choices[0].message.content}"
                    )
                    raise
                try:
                    assert isinstance(new_message, dict)
                    assert isinstance(new_message["memories"], list)
                except AssertionError:
                    logger.error(
                        f"Invalid response format: {response.choices[0].message.content}"
                    )
                    raise
                new_discrete_memories.extend(new_message["memories"])

        # Update the memory to mark it as processed using the vectorstore adapter
        updated_memory = memory.model_copy(update={"discrete_memory_extracted": "t"})
        updated_memories.append(updated_memory)

    if updated_memories:
        await adapter.update_memories(updated_memories)

    if new_discrete_memories:
        long_term_memories = [
            MemoryRecord(
                id=str(ulid.ULID()),
                text=new_memory["text"],
                memory_type=new_memory.get("type", "episodic"),
                topics=new_memory.get("topics", []),
                entities=new_memory.get("entities", []),
                discrete_memory_extracted="t",
            )
            for new_memory in new_discrete_memories
        ]

        await index_long_term_memories(
            long_term_memories,
            deduplicate=deduplicate,
        )
