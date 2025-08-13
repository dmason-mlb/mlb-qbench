"""Qdrant collection schema definitions and setup."""

import os
from typing import Any, Optional

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    TextIndexParams,
    TokenizerType,
    VectorParams,
)

logger = structlog.get_logger()

# Collection names
TEST_DOCS_COLLECTION = "test_docs"
TEST_STEPS_COLLECTION = "test_steps"

# Vector dimensions (OpenAI text-embedding-3-large)
VECTOR_DIM = 3072  # Can be adjusted based on embedding model


def get_client() -> QdrantClient:
    """Get Qdrant client instance."""
    url = os.getenv("QDRANT_URL", "http://localhost:6533")
    # Not using Qdrant Cloud - no API key needed for local instance

    return QdrantClient(
        url=url,
        timeout=int(os.getenv("QDRANT_TIMEOUT", "30"))
    )


def create_collections(client: Optional[QdrantClient] = None, recreate: bool = False) -> None:
    """Create Qdrant collections with proper schema."""
    if client is None:
        client = get_client()

    # Check if collections exist
    collections = client.get_collections().collections
    existing_names = {col.name for col in collections}

    # Create test_docs collection
    if recreate or TEST_DOCS_COLLECTION not in existing_names:
        if TEST_DOCS_COLLECTION in existing_names:
            logger.info("Deleting existing test_docs collection")
            client.delete_collection(TEST_DOCS_COLLECTION)

        logger.info("Creating test_docs collection")
        client.create_collection(
            collection_name=TEST_DOCS_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_DIM,
                distance=Distance.COSINE,
            ),
        )

        # Create payload indexes for filtering
        create_test_docs_indexes(client)

    # Create test_steps collection
    if recreate or TEST_STEPS_COLLECTION not in existing_names:
        if TEST_STEPS_COLLECTION in existing_names:
            logger.info("Deleting existing test_steps collection")
            client.delete_collection(TEST_STEPS_COLLECTION)

        logger.info("Creating test_steps collection")
        client.create_collection(
            collection_name=TEST_STEPS_COLLECTION,
            vectors_config=VectorParams(
                size=VECTOR_DIM,
                distance=Distance.COSINE,
            ),
        )

        # Create payload indexes
        create_test_steps_indexes(client)


def create_test_docs_indexes(client: QdrantClient) -> None:
    """Create payload indexes for test_docs collection."""
    logger.info("Creating indexes for test_docs collection")
    
    # Integer index for testId (primary key)
    client.create_payload_index(
        collection_name=TEST_DOCS_COLLECTION,
        field_name="testId",
        field_schema=PayloadSchemaType.INTEGER,
    )

    # Text indexes for exact and fuzzy matching
    text_index_fields = ["jiraKey", "testCaseId", "testPath", "testType"]
    for field in text_index_fields:
        client.create_payload_index(
            collection_name=TEST_DOCS_COLLECTION,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
        )

    # Array indexes for filtering
    array_index_fields = ["tags", "platforms", "relatedIssues"]
    for field in array_index_fields:
        client.create_payload_index(
            collection_name=TEST_DOCS_COLLECTION,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
        )

    # Keyword indexes for exact matching
    keyword_fields = ["priority", "source", "folderStructure"]
    for field in keyword_fields:
        client.create_payload_index(
            collection_name=TEST_DOCS_COLLECTION,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
        )

    # Full text search on title and description
    client.create_payload_index(
        collection_name=TEST_DOCS_COLLECTION,
        field_name="title",
        field_schema=TextIndexParams(
            type=PayloadSchemaType.TEXT,
            tokenizer=TokenizerType.WORD,
            min_token_len=2,
            max_token_len=20,
            lowercase=True,
        )
    )


def create_test_steps_indexes(client: QdrantClient) -> None:
    """Create payload indexes for test_steps collection."""
    logger.info("Creating indexes for test_steps collection")
    
    # Index for parent document reference by testId
    client.create_payload_index(
        collection_name=TEST_STEPS_COLLECTION,
        field_name="parent_test_id",
        field_schema=PayloadSchemaType.INTEGER,
    )

    # Keep parent_uid for backward compatibility during migration
    client.create_payload_index(
        collection_name=TEST_STEPS_COLLECTION,
        field_name="parent_uid",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    # Index for step number
    client.create_payload_index(
        collection_name=TEST_STEPS_COLLECTION,
        field_name="step_index",
        field_schema=PayloadSchemaType.INTEGER,
    )

    # Full text search on action
    client.create_payload_index(
        collection_name=TEST_STEPS_COLLECTION,
        field_name="action",
        field_schema=TextIndexParams(
            type=PayloadSchemaType.TEXT,
            tokenizer=TokenizerType.WORD,
            min_token_len=2,
            max_token_len=20,
            lowercase=True,
        )
    )


def check_collections_health(client: Optional[QdrantClient] = None) -> dict[str, Any]:
    """Check health and stats of collections."""
    if client is None:
        client = get_client()

    health = {
        "status": "healthy",
        "collections": {}
    }

    try:
        for collection_name in [TEST_DOCS_COLLECTION, TEST_STEPS_COLLECTION]:
            try:
                info = client.get_collection(collection_name)
                health["collections"][collection_name] = {
                    "status": info.status,
                    "vectors_count": info.vectors_count,
                    "points_count": info.points_count,
                    "indexed_vectors_count": info.indexed_vectors_count,
                    "segments_count": info.segments_count,
                    "config": {
                        "vector_size": info.config.params.vectors.size,
                        "distance": info.config.params.vectors.distance,
                    }
                }
            except Exception as e:
                health["collections"][collection_name] = {
                    "status": "error",
                    "error": str(e)
                }
                health["status"] = "degraded"
    except Exception as e:
        health["status"] = "error"
        health["error"] = str(e)

    return health


if __name__ == "__main__":
    # Setup logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Create collections
    logger.info("Setting up Qdrant collections")
    create_collections(recreate=True)

    # Check health
    health = check_collections_health()
    logger.info("Collections health", health=health)
