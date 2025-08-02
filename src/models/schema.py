"""Qdrant collection schema definitions and setup."""

import os
from typing import Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    OptimizersConfig,
    HnswConfig,
    PayloadSchemaType,
    PayloadIndexParams,
    TextIndexParams,
    TokenizerType,
    IntegerIndexParams,
    KeywordIndexParams,
)
import structlog

logger = structlog.get_logger()

# Collection names
TEST_DOCS_COLLECTION = "test_docs"
TEST_STEPS_COLLECTION = "test_steps"

# Vector dimensions (OpenAI text-embedding-3-large)
VECTOR_DIM = 3072  # Can be adjusted based on embedding model

# HNSW parameters optimized for ~25% of corpus initially
HNSW_CONFIG = HnswConfig(
    m=32,  # Number of connections per node
    ef_construct=128,  # Size of dynamic candidate list
    full_scan_threshold=10000,  # Use HNSW for collections > 10k points
    max_indexing_threads=0,  # Use all available cores
    on_disk=False,  # Keep in memory for performance
)

# Optimizer config
OPTIMIZER_CONFIG = OptimizersConfig(
    deleted_threshold=0.2,  # Vacuum when 20% deleted
    vacuum_min_vector_number=1000,  # Don't vacuum small collections
    default_segment_number=2,  # Start with 2 segments
    max_segment_size=200000,  # 200k vectors per segment
    memmap_threshold=100000,  # Use mmap for segments > 100k
    indexing_threshold=20000,  # Start indexing at 20k vectors
    flush_interval_sec=5,  # Flush to disk every 5 seconds
)


def get_client() -> QdrantClient:
    """Get Qdrant client instance."""
    url = os.getenv("QDRANT_URL", "http://localhost:6533")
    api_key = os.getenv("QDRANT_API_KEY")
    
    return QdrantClient(
        url=url,
        api_key=api_key,
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
            hnsw_config=HNSW_CONFIG,
            optimizers_config=OPTIMIZER_CONFIG,
            on_disk_payload=False,  # Keep payload in memory
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
            hnsw_config=HNSW_CONFIG,
            optimizers_config=OPTIMIZER_CONFIG,
            on_disk_payload=False,
        )
        
        # Create payload indexes
        create_test_steps_indexes(client)


def create_test_docs_indexes(client: QdrantClient) -> None:
    """Create payload indexes for test_docs collection."""
    logger.info("Creating indexes for test_docs collection")
    
    # Text indexes for exact and fuzzy matching
    text_index_fields = ["jiraKey", "testCaseId", "testPath", "testType"]
    for field in text_index_fields:
        client.create_payload_index(
            collection_name=TEST_DOCS_COLLECTION,
            field_name=field,
            field_schema=KeywordIndexParams(
                type=PayloadSchemaType.KEYWORD,
                is_tenant=False,
            )
        )
    
    # Array indexes for filtering
    array_index_fields = ["tags", "platforms", "relatedIssues"]
    for field in array_index_fields:
        client.create_payload_index(
            collection_name=TEST_DOCS_COLLECTION,
            field_name=field,
            field_schema=KeywordIndexParams(
                type=PayloadSchemaType.KEYWORD,
                is_tenant=False,
            )
        )
    
    # Keyword indexes for exact matching
    keyword_fields = ["priority", "source", "folderStructure"]
    for field in keyword_fields:
        client.create_payload_index(
            collection_name=TEST_DOCS_COLLECTION,
            field_name=field,
            field_schema=KeywordIndexParams(
                type=PayloadSchemaType.KEYWORD,
                is_tenant=False,
            )
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
    
    # Index for parent document reference
    client.create_payload_index(
        collection_name=TEST_STEPS_COLLECTION,
        field_name="parent_uid",
        field_schema=KeywordIndexParams(
            type=PayloadSchemaType.KEYWORD,
            is_tenant=False,
        )
    )
    
    # Index for step number
    client.create_payload_index(
        collection_name=TEST_STEPS_COLLECTION,
        field_name="step_index",
        field_schema=IntegerIndexParams(
            type=PayloadSchemaType.INTEGER,
            lookup=True,
            range=True,
        )
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


def check_collections_health(client: Optional[QdrantClient] = None) -> Dict[str, Any]:
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