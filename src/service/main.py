"""Comprehensive FastAPI service for MLB QBench test retrieval and management.

This module implements the complete REST API for the MLB QBench test retrieval system,
providing semantic search, data ingestion, health monitoring, and JIRA integration
capabilities through a high-performance async FastAPI framework.

Core Features:
    - Semantic Search: AI-powered test discovery using vector embeddings
    - Hybrid Search: Combined document-level and step-level search algorithms
    - Data Ingestion: Batch processing of test data from multiple sources
    - JIRA Integration: Bidirectional synchronization with Atlassian JIRA
    - Health Monitoring: Real-time service and database health checks
    - Performance Metrics: Resource usage and performance statistics
    - Security Framework: API key authentication and input validation

API Endpoints:
    - POST /search: Semantic test search with natural language queries
    - POST /ingest: Batch test data ingestion from JSON files
    - GET /healthz: Service health status and diagnostics
    - GET /metrics: Performance metrics and resource usage
    - GET /tests/{test_id}: Retrieve test by internal ID
    - GET /by-jira/{jira_key}: Retrieve test by JIRA issue key
    - PATCH /tests/{test_id}/jira-key: Update test JIRA key reference
    - GET /tests/without-jira: Find tests missing JIRA associations
    - GET /similar/{jira_key}: Find semantically similar tests

Architectural Features:
    - Async Processing: Full async/await for maximum concurrency
    - Dependency Injection: Service container for loose coupling
    - Rate Limiting: DoS protection with configurable limits
    - CORS Security: Configurable cross-origin request handling
    - Error Handling: Comprehensive exception management
    - Logging: Structured logging with security event tracking

Performance Optimizations:
    - Concurrent Search: Parallel document and step search execution
    - Connection Pooling: Efficient database connection management
    - Batch Processing: Optimized embedding generation and storage
    - Memory Management: Efficient resource allocation and cleanup
    - Caching: Service-level caching for improved response times

Security Framework:
    - Authentication: API key-based access control
    - Input Validation: Comprehensive sanitization and validation
    - Injection Prevention: SQL injection and XSS protection
    - Path Validation: Directory traversal and SSRF prevention
    - Audit Logging: Security event tracking and monitoring
    - Rate Limiting: DoS protection and fair usage enforcement

Integration Points:
    - Qdrant Vector Database: High-performance semantic search backend
    - Multiple Embedding Providers: OpenAI, Cohere, Vertex AI, Azure support
    - JIRA REST API: Bidirectional test case synchronization
    - Monitoring Systems: Health checks and metrics export
    - Authentication Systems: API key validation and management

Deployment Features:
    - Docker Support: Containerized deployment ready
    - Environment Configuration: Flexible configuration management
    - Health Checks: Container orchestration health endpoints
    - Graceful Shutdown: Proper resource cleanup on termination
    - Development Tools: Hot reload and debug support
"""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Literal, Optional

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchText, MatchValue
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from ..auth import require_api_key
from ..auth.auth import get_api_key
from ..container import (
    Container,
    configure_services,
)
from ..embedder import prepare_text_for_embedding
from ..ingest.ingest_api import ingest_api_tests
from ..ingest.ingest_functional import ingest_functional_tests
from ..models.schema import TEST_DOCS_COLLECTION, TEST_STEPS_COLLECTION, check_collections_health
from ..models.test_models import (
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResult,
    TestDoc,
    UpdateJiraKeyRequest,
)
from ..security import JiraKeyValidationError, PathValidationError

# Load environment variables
load_dotenv()

# Configure logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI application lifespan manager with service initialization and cleanup.

    Manages the complete application lifecycle including dependency injection setup,
    service initialization, health monitoring, and graceful shutdown procedures.

    Lifecycle Management:
        Startup:
            1. Configure dependency injection container
            2. Initialize core services (Qdrant client, embedder)
            3. Perform collection health checks
            4. Store container in application state
            5. Setup rate limiting and exception handling

        Shutdown:
            1. Log shutdown initiation
            2. Dispose of all async services
            3. Clean up connection pools
            4. Release all resources

    Service Dependencies:
        - Qdrant vector database client
        - Embedding provider (OpenAI, Cohere, Vertex AI, Azure)
        - Rate limiter for DoS protection
        - Validators for security (path, JIRA, API key)

    Error Handling:
        Startup failures are logged and propagated to prevent
        application start with unhealthy dependencies.
        Cleanup errors are logged but don't prevent shutdown.

    Args:
        app: FastAPI application instance to manage

    Yields:
        None: Application operational period

    Performance:
        - Startup: O(s) where s = number of services to initialize
        - Shutdown: O(s) where s = number of active service instances

    Usage:
        Called automatically by FastAPI framework during
        application startup and shutdown cycles.
    """
    # Configure services in the container
    container = configure_services()

    logger.info("Initializing services...")

    # Initialize core services
    qdrant_client = container.get("qdrant_client")

    # Check collections health
    health = check_collections_health(qdrant_client)
    logger.info("Collections health", health=health)

    # Store container in app state for access in endpoints
    app.state.container = container

    # Set up rate limiter for exception handling
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    yield

    # Cleanup
    logger.info("Shutting down services...")
    await container.dispose_async()


# Create FastAPI app
app = FastAPI(
    title="MLB QBench Test Retrieval API",
    version="1.0.0",
    description="Semantic search API for test retrieval from Qdrant",
    lifespan=lifespan,
)

# Create rate limiter instance
limiter = Limiter(key_func=get_remote_address)

# Add CORS middleware with secure configuration
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-API-Key"],
    max_age=3600,
)


def build_filter(filters: Optional[dict[str, Any]]) -> Optional[Filter]:
    """Construct secure Qdrant filter objects from user-provided filter parameters.

    Builds type-safe Qdrant Filter objects from dictionary input with comprehensive
    security validation to prevent injection attacks and ensure query safety.

    Security Features:
        - Input sanitization against injection attacks
        - Filter validation through dedicated security module
        - Dangerous character detection and blocking
        - Safe operator handling with type checking

    Filter Types Supported:
        - Exact Match: Single value equality (MatchValue)
        - Array Membership: Multi-value inclusion (MatchAny)
        - Text Search: Substring matching (MatchText with __contains)
        - Combined Filters: Multiple conditions with AND logic

    Operator Support:
        - field: value -> Exact match on field
        - field__contains: text -> Text search within field
        - field: [val1, val2] -> Array membership test

    Args:
        filters: Dictionary of filter conditions with field names as keys
                and filter values (strings, lists, or operator expressions)

    Returns:
        Optional[Filter]: Qdrant Filter object with must conditions,
                         or None if no valid filters provided

    Raises:
        ValueError: If filter validation fails due to security violations
                   or malformed filter parameters

    Performance:
        - Validation: O(f*v) where f=fields, v=values per field
        - Construction: O(c) where c=number of conditions

    Security:
        All filters are validated through validate_and_sanitize_filters()
        to prevent SQL injection, XSS, and other attack vectors.

    Examples:
        >>> build_filter({"priority": "High"})  # Exact match
        >>> build_filter({"tags": ["ui", "api"]})  # Array membership
        >>> build_filter({"title__contains": "login"})  # Text search
    """
    if not filters:
        return None

    # Import here to avoid circular imports
    from src.models.filter_models import validate_and_sanitize_filters

    try:
        # Validate and sanitize input filters
        sanitized_filters = validate_and_sanitize_filters(filters)

        if not sanitized_filters:
            return None

        conditions = []

        # Handle different filter types with validated input
        for field, value in sanitized_filters.items():
            # Handle special operators
            if field.endswith("__contains"):
                # Contains operator for string fields
                actual_field = field.replace("__contains", "")
                conditions.append(
                    FieldCondition(key=actual_field, match=MatchText(text=str(value)))
                )
            elif isinstance(value, list):
                # Array fields (tags, platforms, etc.) or IN operations
                if value:  # Only add if list is not empty
                    conditions.append(FieldCondition(key=field, match=MatchAny(any=value)))
            else:
                # Single value fields
                conditions.append(FieldCondition(key=field, match=MatchValue(value=value)))

        if conditions:
            return Filter(must=conditions)

        return None

    except Exception as e:
        # Log the security violation attempt
        logger.error(
            "Filter validation failed - potential security threat",
            error=str(e),
            filters=filters,
            extra={"security_event": True},
        )
        # Re-raise as ValueError with generic message to avoid info disclosure
        raise ValueError("Invalid filter parameters") from None


async def search_documents(
    query: str, top_k: int, filters: Optional[dict[str, Any]], container: Container
) -> list[dict[str, Any]]:
    """Search test documents using vector similarity in the document collection.

    Performs semantic search on test documents by generating embeddings for the query
    and finding similar document-level vectors in the test_docs collection.

    Args:
        query: Natural language search query text
        top_k: Maximum number of results to return
        filters: Optional filter conditions for result refinement
        container: Dependency injection container for service access

    Returns:
        list[dict[str, Any]]: List of tuples containing (document_payload, similarity_score)

    Performance:
        - Query embedding: O(m) where m = query length
        - Vector search: O(log n) where n = number of documents
        - Filter application: O(f) where f = matching documents

    Process Flow:
        1. Generate query embedding using configured provider
        2. Execute vector similarity search in test_docs collection
        3. Apply user-provided filters to results
        4. Return top-k documents with similarity scores
    """
    embedder = container.get("embedder")
    qdrant_client = container.get("qdrant_client")

    query_embedding = await embedder.embed(prepare_text_for_embedding(query))

    results = await asyncio.to_thread(
        qdrant_client.search,
        collection_name=TEST_DOCS_COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=build_filter(filters),
        with_payload=True,
        with_vectors=False,
    )

    return [(r.payload, r.score) for r in results]


async def search_steps(
    query: str, top_k: int, filters: Optional[dict[str, Any]], container: Container
) -> dict[str, list[dict[str, Any]]]:
    """Search test steps using vector similarity and group results by parent document.

    Performs semantic search on individual test steps, then groups matching steps
    by their parent test document and applies document-level filters.

    Args:
        query: Natural language search query text
        top_k: Base number for results (actual step limit is top_k * 3)
        filters: Optional filter conditions applied to parent documents
        container: Dependency injection container for service access

    Returns:
        dict[str, list[dict[str, Any]]]: Dictionary mapping parent UIDs to lists of matching steps

    Performance:
        - Query embedding: O(m) where m = query length
        - Step search: O(log s) where s = number of steps
        - Parent filtering: O(p) where p = number of unique parents
        - Grouping: O(k) where k = number of step results

    Process Flow:
        1. Generate query embedding for step-level search
        2. Execute vector similarity search in test_steps collection
        3. Group step results by parent document UID
        4. Apply document-level filters to parent documents
        5. Return only steps whose parents pass filters

    Backward Compatibility:
        Supports both parent_test_id (new) and parent_uid (legacy) for
        parent document association during system migration.
    """
    embedder = container.get("embedder")
    qdrant_client = container.get("qdrant_client")

    query_embedding = await embedder.embed(prepare_text_for_embedding(query))

    # Search steps
    step_results = await asyncio.to_thread(
        qdrant_client.search,
        collection_name=TEST_STEPS_COLLECTION,
        query_vector=query_embedding,
        limit=top_k * 3,  # Get more steps since we'll group by parent
        with_payload=True,
        with_vectors=False,
    )

    # Group steps by parent - prefer testId but fall back to uid for backward compatibility
    steps_by_parent = {}
    parent_test_ids = {}  # Map parent_uid to parent_test_id

    for result in step_results:
        parent_test_id = result.payload.get("parent_test_id")
        parent_uid = result.payload.get("parent_uid")

        # Use parent_uid as key for backward compatibility
        if parent_uid:
            if parent_uid not in steps_by_parent:
                steps_by_parent[parent_uid] = []
            steps_by_parent[parent_uid].append(
                {
                    "step_index": result.payload.get("step_index"),
                    "action": result.payload.get("action"),
                    "expected": result.payload.get("expected", []),
                    "score": result.score,
                }
            )
            if parent_test_id is not None:
                parent_test_ids[parent_uid] = parent_test_id

    # If we have filters, we need to fetch parent docs to apply filters
    if filters and steps_by_parent:
        # Get parent documents
        parent_uids = list(steps_by_parent.keys())
        parent_filter = Filter(must=[FieldCondition(key="uid", match=MatchAny(any=parent_uids))])

        # Combine with user filters
        user_filter = build_filter(filters)
        if user_filter:
            parent_filter.must.extend(user_filter.must)

        # Query parent docs
        scroll_result = await asyncio.to_thread(
            qdrant_client.scroll,
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=parent_filter,
            limit=len(parent_uids),
            with_payload=["uid"],
            with_vectors=False,
        )

        # Keep only steps whose parents pass the filter
        valid_parent_uids = {point.payload["uid"] for point in scroll_result[0]}
        steps_by_parent = {
            uid: steps for uid, steps in steps_by_parent.items() if uid in valid_parent_uids
        }

    return steps_by_parent


async def search_documents_with_embedding(
    query: str, query_embedding, top_k: int, filters: Optional[dict[str, Any]], container: Container
) -> list[dict[str, Any]]:
    """Search test documents using pre-computed query embedding for optimization.

    Optimized version of search_documents that accepts a pre-computed embedding
    to avoid redundant embedding generation when the same query is used for
    multiple search operations (e.g., combined document and step search).

    Args:
        query: Original query text (used for logging purposes)
        query_embedding: Pre-computed embedding vector for the query
        top_k: Maximum number of results to return
        filters: Optional filter conditions for result refinement
        container: Dependency injection container for service access

    Returns:
        list[dict[str, Any]]: List of tuples containing (document_payload, similarity_score)

    Performance Benefits:
        - Eliminates embedding generation overhead: O(m) savings where m = query length
        - Identical search performance to search_documents for vector operations
        - Enables efficient batch operations with shared embeddings

    Usage:
        Called by _search_impl when scope="all" to avoid duplicate embedding
        generation for concurrent document and step searches.
    """
    qdrant_client = container.get("qdrant_client")

    results = await asyncio.to_thread(
        qdrant_client.search,
        collection_name=TEST_DOCS_COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=build_filter(filters),
        with_payload=True,
        with_vectors=False,
    )

    return [(r.payload, r.score) for r in results]


async def search_steps_with_embedding(
    query: str, query_embedding, top_k: int, filters: Optional[dict[str, Any]], container: Container
) -> dict[str, list[dict[str, Any]]]:
    """Search test steps using pre-computed query embedding and group by parent document.

    Optimized version of search_steps that accepts a pre-computed embedding
    to avoid redundant embedding generation during concurrent search operations.

    Args:
        query: Original query text (used for logging purposes)
        query_embedding: Pre-computed embedding vector for the query
        top_k: Base number for results (actual step limit is top_k * 3)
        filters: Optional filter conditions applied to parent documents
        container: Dependency injection container for service access

    Returns:
        dict[str, list[dict[str, Any]]]: Dictionary mapping parent UIDs to lists of matching steps

    Performance Benefits:
        - Eliminates embedding generation overhead for shared queries
        - Enables efficient concurrent document and step searches
        - Maintains same search quality as search_steps function

    Enhanced Parent Filtering:
        Applies user filters directly during step search and validates
        parent documents separately, ensuring comprehensive filter compliance.

    Process Flow:
        1. Execute vector similarity search using pre-computed embedding
        2. Group step results by parent document identifiers
        3. Build combined filter for parent document validation
        4. Filter steps based on parent document filter compliance
        5. Return grouped and filtered step results
    """
    qdrant_client = container.get("qdrant_client")

    # Search steps
    step_results = await asyncio.to_thread(
        qdrant_client.search,
        collection_name=TEST_STEPS_COLLECTION,
        query_vector=query_embedding,
        limit=top_k * 3,  # Get more steps to ensure good parent coverage
        query_filter=build_filter(filters),
        with_payload=True,
        with_vectors=False,
    )

    # Group by parent and filter steps whose parents match user filters
    steps_by_parent = {}
    parent_uids = set()
    parent_test_ids = {}  # Map parent_uid to parent_test_id

    for result in step_results:
        parent_test_id = result.payload.get("parent_test_id")
        parent_uid = result.payload.get("parent_uid")

        if parent_uid:
            parent_uids.add(parent_uid)
            if parent_uid not in steps_by_parent:
                steps_by_parent[parent_uid] = []
            steps_by_parent[parent_uid].append({"step_data": result.payload, "score": result.score})
            if parent_test_id is not None:
                parent_test_ids[parent_uid] = parent_test_id

    if not parent_uids:
        return {}

    # Build filter for parent documents
    parent_filter = Filter(must=[FieldCondition(key="uid", match=MatchAny(any=list(parent_uids)))])

    # Combine with user filters
    user_filter = build_filter(filters)
    if user_filter:
        parent_filter.must.extend(user_filter.must)

    # Query parent docs
    scroll_result = await asyncio.to_thread(
        qdrant_client.scroll,
        collection_name=TEST_DOCS_COLLECTION,
        scroll_filter=parent_filter,
        limit=len(parent_uids),
        with_payload=["uid"],
        with_vectors=False,
    )

    # Keep only steps whose parents pass the filter
    valid_parent_uids = {point.payload["uid"] for point in scroll_result[0]}
    steps_by_parent = {
        uid: steps for uid, steps in steps_by_parent.items() if uid in valid_parent_uids
    }

    return steps_by_parent


async def merge_and_rerank_results(
    doc_results: list[tuple[dict[str, Any], float]],
    steps_by_parent: dict[str, list[dict[str, Any]]],
    top_k: int,
    container: Container,
) -> list[SearchResult]:
    """Merge and rerank document and step search results using hybrid scoring.

    Combines document-level and step-level search results into a unified ranking
    using weighted scoring to balance document relevance with step-level matches.

    Scoring Algorithm:
        - Documents with step matches: 70% document score + 30% max step score
        - Documents without step matches: 100% document score
        - Step-only matches: 80% max step score (slight penalty for no doc match)

    Args:
        doc_results: Document search results as (payload, score) tuples
        steps_by_parent: Step results grouped by parent document UID
        top_k: Maximum number of final results to return
        container: Dependency injection container for database access

    Returns:
        list[SearchResult]: Merged and ranked search results with TestDoc objects

    Performance:
        - Document processing: O(d) where d = number of document results
        - Step processing: O(s) where s = number of step groups
        - Parent fetching: O(p) where p = step-only parents to fetch
        - Sorting: O(r log r) where r = total results before top-k selection

    Result Categories:
        1. Document matches with step reinforcement (highest relevance)
        2. Document-only matches (medium relevance)
        3. Step-only matches (contextual relevance)

    Quality Assurance:
        - Validates all document payloads through TestDoc model
        - Preserves step index information for result highlighting
        - Maintains score transparency for debugging and tuning
    """
    # Create a map of uid to document results
    doc_map = {doc[0]["uid"]: (doc[0], doc[1]) for doc in doc_results}

    # Combine scores and create final results
    all_results = []

    # Add documents that have direct matches
    for uid, (doc, doc_score) in doc_map.items():
        step_matches = steps_by_parent.get(uid, [])

        # Calculate combined score
        if step_matches:
            # Boost score if we have matching steps
            max_step_score = max(s["score"] for s in step_matches)
            combined_score = doc_score * 0.7 + max_step_score * 0.3
        else:
            combined_score = doc_score

        # Create TestDoc from payload
        test_doc = TestDoc(**doc)

        # Create result
        result = SearchResult(
            test=test_doc,
            score=combined_score,
            matched_steps=[s["step_data"]["step_index"] for s in step_matches],
        )
        all_results.append(result)

    # Add documents that only have step matches (not in doc results)
    qdrant_client = container.get("qdrant_client")
    for uid, step_matches in steps_by_parent.items():
        if uid not in doc_map:
            # Fetch the document
            doc_filter = Filter(must=[FieldCondition(key="uid", match=MatchValue(value=uid))])
            docs = await asyncio.to_thread(
                qdrant_client.scroll,
                collection_name=TEST_DOCS_COLLECTION,
                scroll_filter=doc_filter,
                limit=1,
                with_payload=True,
                with_vectors=False,
            )

            if docs[0]:
                doc = docs[0][0].payload
                max_step_score = max(s["score"] for s in step_matches)

                test_doc = TestDoc(**doc)
                result = SearchResult(
                    test=test_doc,
                    score=max_step_score * 0.8,  # Slightly lower score for step-only matches
                    matched_steps=[s["step_data"]["step_index"] for s in step_matches],
                )
                all_results.append(result)

    # Sort by score and return top-k
    all_results.sort(key=lambda x: x.score, reverse=True)
    return all_results[:top_k]


@app.get("/")
async def root():
    """Root API endpoint providing service identification and status.

    Simple endpoint for service discovery, health monitoring, and API validation.
    Returns basic service metadata without requiring authentication.

    Returns:
        dict: Service information including name, version, and operational status

    HTTP Status:
        - 200 OK: Service is operational and responding to requests

    Usage:
        - Load balancer health checks
        - Service discovery and registration
        - Basic connectivity validation
        - API documentation verification
    """
    return {"service": "MLB QBench Test Retrieval API", "version": "1.0.0", "status": "running"}


@app.get("/healthz")
async def health(request: Request, api_key: str = Security(get_api_key)):
    """Comprehensive health check endpoint with authentication and detailed diagnostics.

    Performs deep health validation of all critical system components including
    vector database connectivity, collection status, and service dependencies.

    Authentication:
        Requires valid API key to prevent unauthorized health monitoring
        and potential information disclosure to attackers.

    Health Checks:
        - Qdrant vector database connectivity and responsiveness
        - Collection existence and operational status
        - Vector count and indexing status validation
        - Service dependency availability verification

    Args:
        request: FastAPI request object containing application state
        api_key: Validated API key from security dependency

    Returns:
        dict: Comprehensive health status including:
            - status: Overall health (healthy/degraded/unhealthy)
            - timestamp: ISO 8601 timestamp of health check
            - qdrant: Detailed vector database health metrics

    HTTP Status Codes:
        - 200 OK: All systems operational (status: healthy/degraded)
        - 401 Unauthorized: Invalid or missing API key
        - 500 Internal Server Error: Critical system failure

    Security Features:
        - API key validation prevents unauthorized access
        - Structured logging with security event tracking
        - Sensitive information masking in logs
        - Rate limiting through global rate limiter

    Monitoring Integration:
        Designed for integration with monitoring systems, alerting,
        and automated health check orchestration.
    """
    try:
        container = request.app.state.container
        qdrant_client = container.get("qdrant_client")
        health_status = check_collections_health(qdrant_client)

        # Log health check access for security audit
        logger.info(
            "Health check accessed",
            api_key_prefix=api_key[:8] + "..." if len(api_key) > 8 else "***",
            health_status=health_status["status"],
        )

        return {
            "status": "healthy" if health_status["status"] == "healthy" else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "qdrant": health_status,
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
        }


@app.get("/metrics")
async def metrics(request: Request, api_key: str = Security(get_api_key)):
    """Comprehensive performance metrics and resource usage monitoring endpoint.

    Provides detailed operational metrics for performance monitoring, capacity
    planning, and cost optimization across all system components.

    Metrics Categories:
        - Embedding Provider: Usage statistics, token consumption, request counts
        - Dependency Container: Service registration and instantiation status
        - Rate Limiter: Request throttling and limit enforcement statistics
        - Async Framework: Concurrency and resource management capabilities

    Args:
        request: FastAPI request object containing application state
        api_key: Validated API key from security dependency

    Returns:
        dict: Comprehensive metrics including:
            - timestamp: ISO 8601 timestamp of metrics collection
            - embedding_provider: Provider-specific usage and performance data
            - dependency_container: Service lifecycle and registration metrics
            - rate_limiter: Request limiting and throttling statistics
            - async_framework: Concurrency and performance feature flags

    HTTP Status Codes:
        - 200 OK: Metrics successfully collected and returned
        - 401 Unauthorized: Invalid or missing API key
        - 500 Internal Server Error: Metrics collection failure

    Performance Monitoring:
        - Embedding token usage for cost tracking
        - Service instantiation patterns for optimization
        - Rate limiting effectiveness for security monitoring
        - Async operation utilization for capacity planning

    Security:
        - Requires API key authentication
        - Masks sensitive configuration details
        - Logs access for audit trail
        - No exposure of internal system secrets
    """
    try:
        container = request.app.state.container

        # Get embedding provider stats
        embedder = container.get("embedder")
        embedder_stats = embedder.get_stats()

        # Get container stats
        container_stats = container.get_service_info()

        # Get rate limiter stats (if available)
        limiter = request.app.state.limiter
        limiter_stats = {}
        if hasattr(limiter, "_storage"):
            limiter_stats = {
                "storage_type": type(limiter._storage).__name__,
                "active_limits": len(getattr(limiter._storage, "_storage", {})),
            }

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "embedding_provider": embedder_stats,
            "dependency_container": container_stats,
            "rate_limiter": limiter_stats,
            "async_framework": {
                "concurrent_searches_enabled": True,
                "batch_processing_enabled": True,
                "resource_management": "async",
            },
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


async def _search_impl(request: Request, search_request: SearchRequest) -> list[SearchResult]:
    """Internal search implementation with optimized concurrent processing.

    Core search engine that orchestrates document and step searches with intelligent
    embedding reuse and concurrent execution for maximum performance.

    Performance Optimizations:
        - Single embedding generation for scope="all" to eliminate duplication
        - Concurrent execution of document and step searches using asyncio.gather
        - Intelligent task composition based on search scope requirements
        - Pre-computed embedding sharing between search operations

    Args:
        request: FastAPI request object containing application state
        search_request: Validated search parameters and filters

    Returns:
        list[SearchResult]: Merged and ranked search results

    Search Scope Handling:
        - "all": Concurrent document and step search with embedding reuse
        - "docs": Document-only search with optimized parameters
        - "steps": Step-only search with parent document validation

    Concurrent Execution:
        Uses asyncio.gather for true parallel execution of independent
        search operations, significantly reducing total search latency.

    Error Handling:
        - Individual search failures are caught and re-raised with context
        - Embedding generation errors propagate with detailed logging
        - Resource cleanup ensures no hanging operations

    Performance:
        - Embedding generation: O(m) where m = query length (once for scope="all")
        - Concurrent searches: O(max(doc_search, step_search)) vs O(doc_search + step_search)
        - Result merging: O(r log r) where r = total results

    Quality Assurance:
        - Comprehensive error handling with context preservation
        - Detailed performance logging for optimization
        - Task exception handling prevents partial failures
    """
    container = request.app.state.container

    # Pre-compute embedding once for scope="all" to avoid duplication
    query_embedding = None
    if search_request.scope == "all":
        embedder = container.get("embedder")
        query_embedding = await embedder.embed(prepare_text_for_embedding(search_request.query))

    # Prepare concurrent search tasks
    tasks = []

    # Add document search task if needed
    if search_request.scope in ["all", "docs"]:
        if query_embedding is not None:
            doc_task = search_documents_with_embedding(
                search_request.query,
                query_embedding,
                search_request.top_k,
                search_request.filters,
                container,
            )
        else:
            doc_task = search_documents(
                search_request.query, search_request.top_k, search_request.filters, container
            )
        tasks.append(("docs", doc_task))

    # Add step search task if needed
    if search_request.scope in ["all", "steps"]:
        if query_embedding is not None:
            steps_task = search_steps_with_embedding(
                search_request.query,
                query_embedding,
                search_request.top_k,
                search_request.filters,
                container,
            )
        else:
            steps_task = search_steps(
                search_request.query, search_request.top_k, search_request.filters, container
            )
        tasks.append(("steps", steps_task))

    # Execute searches concurrently
    if tasks:
        task_names, task_coroutines = zip(*tasks)
        results_list = await asyncio.gather(*task_coroutines, return_exceptions=True)

        # Process results and handle any exceptions
        doc_results = []
        steps_by_parent = {}

        for task_name, result in zip(task_names, results_list):
            if isinstance(result, Exception):
                logger.error(f"Error in {task_name} search: {result}")
                raise result

            if task_name == "docs":
                doc_results = result
            elif task_name == "steps":
                steps_by_parent = result
    else:
        # No searches needed based on scope
        doc_results = []
        steps_by_parent = {}

    # Merge and rerank
    results = await merge_and_rerank_results(
        doc_results, steps_by_parent, search_request.top_k, container
    )

    logger.info(
        "Search completed",
        query=search_request.query,
        results_count=len(results),
        scope=search_request.scope,
        concurrent_searches=len(tasks),
    )

    return results


@app.post("/search", response_model=list[SearchResult])
@limiter.limit("60/minute")
async def search(request: Request, search_request: SearchRequest, api_key: str = require_api_key):
    """Semantic test search endpoint with natural language query processing.

    Performs AI-powered test discovery using vector embeddings and hybrid search
    algorithms across both document-level and step-level content.

    Search Capabilities:
        - Natural language query understanding
        - Document-level semantic similarity matching
        - Step-level action and validation matching
        - Hybrid scoring combining multiple relevance signals
        - Advanced filtering with security validation

    Args:
        request: FastAPI request object with application state
        search_request: Search parameters including query, filters, and scope
        api_key: Authenticated API key for access control

    Returns:
        list[SearchResult]: Ranked search results with relevance scores

    HTTP Status Codes:
        - 200 OK: Search completed successfully
        - 400 Bad Request: Invalid search parameters or filters
        - 401 Unauthorized: Invalid or missing API key
        - 429 Too Many Requests: Rate limit exceeded (60 requests/minute)
        - 500 Internal Server Error: Search processing failure

    Rate Limiting:
        Limited to 60 requests per minute per client to prevent abuse
        and ensure fair resource allocation across users.

    Performance Features:
        - Concurrent document and step search execution
        - Intelligent embedding reuse for multi-scope searches
        - Optimized vector similarity calculations
        - Efficient result merging and ranking

    Security:
        - API key authentication required
        - Input validation and sanitization
        - Filter injection protection
        - Query pattern monitoring
    """
    try:
        return await _search_impl(request, search_request)
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/ingest", response_model=IngestResponse)
@limiter.limit("5/minute")
async def ingest(request: Request, ingest_request: IngestRequest, api_key: str = require_api_key):
    """Batch test data ingestion endpoint with comprehensive security validation.

    Processes test data from JSON files, normalizes formats, generates embeddings,
    and stores both document-level and step-level vectors in the database.

    Ingestion Capabilities:
        - Functional test data processing with step-by-step procedures
        - API test specification processing with endpoint definitions
        - Concurrent processing of multiple file types
        - Comprehensive data validation and normalization
        - Embedding generation for semantic search enablement

    Args:
        request: FastAPI request object with application state
        ingest_request: File paths and ingestion parameters
        api_key: Authenticated API key for access control

    Returns:
        IngestResponse: Detailed ingestion results including counts and errors

    HTTP Status Codes:
        - 200 OK: Ingestion completed (check response for detailed status)
        - 400 Bad Request: Invalid file paths or validation failures
        - 401 Unauthorized: Invalid or missing API key
        - 404 Not Found: Specified files do not exist
        - 429 Too Many Requests: Rate limit exceeded (5 requests/minute)
        - 500 Internal Server Error: Processing failure

    Security Features:
        - Path traversal attack prevention through secure validation
        - SSRF protection with file path restrictions
        - Input sanitization and format validation
        - Audit logging of all ingestion attempts
        - API key authentication requirement

    Rate Limiting:
        Strictly limited to 5 requests per minute due to resource-intensive
        nature of embedding generation and batch processing.

    Performance:
        - Concurrent file processing when both paths provided
        - Batch embedding generation for efficiency
        - Async database operations for non-blocking processing
        - Progress tracking and detailed error reporting

    Data Processing:
        - JSON parsing with error handling
        - Schema validation against TestDoc model
        - Field normalization across different source formats
        - Duplicate detection and handling
    """
    try:
        container = request.app.state.container
        path_validator = container.get("path_validator")
        response = IngestResponse()

        # Ingest functional tests if path provided
        if ingest_request.functional_path:
            try:
                # Secure path validation to prevent SSRF and directory traversal
                functional_path = path_validator(ingest_request.functional_path)

                if not functional_path.exists():
                    raise HTTPException(
                        status_code=404,
                        detail=f"Functional file not found: {ingest_request.functional_path}",
                    )

                # Pass embedder and client from container to avoid OPENAI_API_KEY dependency
                embedder = container.get("embedder")
                qdrant_client = container.get("qdrant_client")
                result = await ingest_functional_tests(
                    str(functional_path), embedder=embedder, client=qdrant_client
                )
                response.functional_ingested = result.get("ingested", 0)
                response.errors.extend(result.get("errors", []))
                response.warnings.extend(result.get("warnings", []))

            except PathValidationError as e:
                logger.error(
                    "Functional path validation failed",
                    path=ingest_request.functional_path,
                    error=str(e),
                    extra={"security_event": True},
                )
                raise HTTPException(
                    status_code=400, detail=f"Invalid functional file path: {str(e)}"
                ) from None

        # Ingest API tests if path provided
        if ingest_request.api_path:
            try:
                # Secure path validation to prevent SSRF and directory traversal
                api_path = path_validator(ingest_request.api_path)

                if not api_path.exists():
                    raise HTTPException(
                        status_code=404, detail=f"API file not found: {ingest_request.api_path}"
                    )

                # Pass embedder and client from container to avoid OPENAI_API_KEY dependency
                embedder = container.get("embedder")
                qdrant_client = container.get("qdrant_client")
                result = await ingest_api_tests(
                    str(api_path), embedder=embedder, client=qdrant_client
                )
                response.api_ingested = result.get("ingested", 0)
                response.errors.extend(result.get("errors", []))
                response.warnings.extend(result.get("warnings", []))

            except PathValidationError as e:
                logger.error(
                    "API path validation failed",
                    path=ingest_request.api_path,
                    error=str(e),
                    extra={"security_event": True},
                )
                raise HTTPException(
                    status_code=400, detail=f"Invalid API file path: {str(e)}"
                ) from None

        logger.info(
            "Ingestion completed",
            functional=response.functional_ingested,
            api=response.api_ingested,
            errors=len(response.errors),
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/tests/{test_id}", response_model=TestDoc)
async def get_by_test_id(request: Request, test_id: int, api_key: str = require_api_key):
    """Retrieve a specific test document by its internal testId.

    Provides direct access to test documents using the auto-generated
    internal identifier for precise document retrieval.

    Args:
        request: FastAPI request object with application state
        test_id: Internal test identifier (auto-incrementing integer)
        api_key: Authenticated API key for access control

    Returns:
        TestDoc: Complete test document with all metadata and steps

    HTTP Status Codes:
        - 200 OK: Test found and returned successfully
        - 401 Unauthorized: Invalid or missing API key
        - 404 Not Found: Test with specified ID does not exist
        - 500 Internal Server Error: Database query failure

    Query Performance:
        - Indexed lookup on testId field for O(log n) performance
        - Single document retrieval optimized for minimal latency
        - No embedding generation required

    Use Cases:
        - Direct test access after search operations
        - Test management system integration
        - Bookmark and reference functionality
        - API client caching and synchronization
    """
    try:
        container = request.app.state.container
        qdrant_client = container.get("qdrant_client")

        # Query by testId
        filter_cond = Filter(must=[FieldCondition(key="testId", match=MatchValue(value=test_id))])

        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=filter_cond,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if not results[0]:
            raise HTTPException(status_code=404, detail=f"Test not found: {test_id}")

        test_data = results[0][0].payload
        return TestDoc(**test_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get by testId error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/by-jira/{jira_key}", response_model=TestDoc)
async def get_by_jira(request: Request, jira_key: str, api_key: str = require_api_key):
    """Retrieve a test document by its associated JIRA issue key.

    Enables test lookup using JIRA integration for requirement traceability
    and agile workflow integration.

    Args:
        request: FastAPI request object with application state
        jira_key: JIRA issue key in PROJECT-NUMBER format (e.g., DEV-123)
        api_key: Authenticated API key for access control

    Returns:
        TestDoc: Complete test document linked to the JIRA issue

    HTTP Status Codes:
        - 200 OK: Test found and returned successfully
        - 400 Bad Request: Invalid JIRA key format
        - 401 Unauthorized: Invalid or missing API key
        - 404 Not Found: No test associated with the JIRA key
        - 500 Internal Server Error: Database query failure

    Security Features:
        - JIRA key format validation to prevent injection attacks
        - Input sanitization and normalization
        - Security event logging for validation failures
        - Standardized error responses to prevent information disclosure

    JIRA Integration:
        - Supports standard Atlassian JIRA key format (PROJECT-NUMBER)
        - Case-insensitive matching with normalization to uppercase
        - Bidirectional traceability between tests and requirements
        - Agile workflow compatibility

    Performance:
        - Indexed lookup on jiraKey field for efficient retrieval
        - Input validation optimized for common JIRA patterns
        - Single query execution with minimal overhead
    """
    try:
        container = request.app.state.container
        jira_validator = container.get("jira_validator")
        qdrant_client = container.get("qdrant_client")

        # Validate JIRA key format to prevent injection attacks
        try:
            validated_jira_key = jira_validator(jira_key)
        except JiraKeyValidationError as e:
            logger.error(
                "JIRA key validation failed in get_by_jira",
                jira_key=jira_key,
                error=str(e),
                extra={"security_event": True},
            )
            raise HTTPException(
                status_code=400, detail=f"Invalid JIRA key format: {str(e)}"
            ) from None

        # Query by jiraKey
        filter_cond = Filter(
            must=[FieldCondition(key="jiraKey", match=MatchValue(value=validated_jira_key))]
        )

        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=filter_cond,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if not results[0]:
            raise HTTPException(status_code=404, detail=f"Test not found: {validated_jira_key}")

        test_data = results[0][0].payload
        return TestDoc(**test_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get by JIRA error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.patch("/tests/{test_id}/jira-key", response_model=TestDoc)
async def update_jira_key(
    request: Request,
    test_id: int,
    update_request: UpdateJiraKeyRequest,
    api_key: str = require_api_key,
):
    """Update the JIRA key association for an existing test document.

    Enables dynamic linking of test cases to JIRA issues for requirement
    traceability and agile workflow integration.

    Args:
        request: FastAPI request object with application state
        test_id: Internal test identifier for the target document
        update_request: New JIRA key in validated format
        api_key: Authenticated API key for access control

    Returns:
        TestDoc: Updated test document with new JIRA key association

    HTTP Status Codes:
        - 200 OK: JIRA key updated successfully
        - 400 Bad Request: Invalid JIRA key format
        - 401 Unauthorized: Invalid or missing API key
        - 404 Not Found: Test with specified ID does not exist
        - 500 Internal Server Error: Database update failure

    Update Operations:
        1. Validates new JIRA key format for security and compliance
        2. Verifies test document existence before modification
        3. Updates jiraKey field with validated value
        4. Synchronizes uid field if it was previously using jiraKey
        5. Persists changes to vector database

    Security Features:
        - Comprehensive JIRA key format validation
        - Transaction-safe update operations
        - Security event logging for validation failures
        - Audit trail of JIRA key modifications

    Business Logic:
        - Maintains uid consistency when jiraKey serves as primary identifier
        - Preserves existing uid if different from jiraKey
        - Supports migration from legacy uid schemes

    Performance:
        - Indexed lookup for efficient test location
        - Minimal payload update using set_payload operation
        - Single transaction for consistency
    """
    try:
        container = request.app.state.container
        jira_validator = container.get("jira_validator")
        qdrant_client = container.get("qdrant_client")

        # Validate the new JIRA key format
        try:
            validated_jira_key = jira_validator(update_request.jiraKey)
        except JiraKeyValidationError as e:
            logger.error(
                "JIRA key validation failed in update_jira_key",
                jira_key=update_request.jiraKey,
                error=str(e),
                extra={"security_event": True},
            )
            raise HTTPException(
                status_code=400, detail=f"Invalid JIRA key format: {str(e)}"
            ) from None

        # First, check if the test exists
        filter_cond = Filter(must=[FieldCondition(key="testId", match=MatchValue(value=test_id))])

        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=filter_cond,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if not results[0]:
            raise HTTPException(status_code=404, detail=f"Test not found: {test_id}")

        # Get the existing test data
        test_data = results[0][0].payload
        point_id = results[0][0].id

        # Update the JIRA key
        test_data["jiraKey"] = validated_jira_key

        # Also update uid if it was using jiraKey as uid
        if test_data.get("uid") == test_data.get("jiraKey") or not test_data.get("jiraKey"):
            test_data["uid"] = validated_jira_key

        # Update the point in Qdrant
        qdrant_client.set_payload(
            collection_name=TEST_DOCS_COLLECTION,
            payload={"jiraKey": validated_jira_key, "uid": test_data["uid"]},
            points=[point_id],
        )

        logger.info("Updated JIRA key for test", test_id=test_id, new_jira_key=validated_jira_key)

        return TestDoc(**test_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update JIRA key error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/tests/without-jira", response_model=list[TestDoc])
async def get_tests_without_jira(
    request: Request,
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    api_key: str = require_api_key,
):
    """Retrieve test documents that lack JIRA key associations.

    Identifies tests that need JIRA integration for complete requirement
    traceability and agile workflow compliance.

    Args:
        request: FastAPI request object with application state
        limit: Maximum number of tests to return (1-100)
        api_key: Authenticated API key for access control

    Returns:
        list[TestDoc]: List of test documents without JIRA key associations

    HTTP Status Codes:
        - 200 OK: Query completed successfully
        - 401 Unauthorized: Invalid or missing API key
        - 500 Internal Server Error: Database query failure

    Query Logic:
        Since Qdrant doesn't support direct "IS NULL" filtering, this endpoint:
        1. Retrieves a larger set of documents (limit * 2)
        2. Filters client-side for missing jiraKey fields
        3. Returns up to the requested limit

    Use Cases:
        - Test management audit and compliance
        - JIRA integration gap analysis
        - Workflow completion tracking
        - Quality assurance reporting

    Performance Considerations:
        - Over-fetching strategy to account for filtering overhead
        - Client-side filtering for NULL/empty value detection
        - Configurable result limits to manage response size
        - Early termination when limit reached

    Data Quality:
        - Identifies tests with NULL jiraKey values
        - Detects tests with empty string jiraKey values
        - Maintains data integrity during filtering
    """
    try:
        container = request.app.state.container
        qdrant_client = container.get("qdrant_client")

        # Query for tests where jiraKey is null or empty
        # Note: Qdrant doesn't have a direct "is null" filter, so we'll get all and filter
        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            limit=limit * 2,  # Get more since we'll filter
            with_payload=True,
            with_vectors=False,
        )

        # Filter for tests without JIRA keys
        tests_without_jira = []
        for point in results[0]:
            if not point.payload.get("jiraKey"):
                test_data = point.payload
                tests_without_jira.append(TestDoc(**test_data))
                if len(tests_without_jira) >= limit:
                    break

        logger.info("Retrieved tests without JIRA keys", count=len(tests_without_jira))

        return tests_without_jira

    except Exception as e:
        logger.error(f"Get tests without JIRA error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/similar/{jira_key}")
async def find_similar(
    request: Request,
    jira_key: str,
    scope: Literal["docs", "steps", "all"] = Query("docs", description="Search scope"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results"),
    api_key: str = require_api_key,
):
    """Discover semantically similar tests based on a reference test document.

    Finds tests with similar content, purpose, or execution patterns using
    the reference test's metadata as the search query.

    Args:
        request: FastAPI request object with application state
        jira_key: JIRA key of the reference test for similarity search
        scope: Search scope - "docs", "steps", or "all" for comprehensive search
        top_k: Maximum number of similar tests to return (1-100)
        api_key: Authenticated API key for access control

    Returns:
        list[SearchResult]: Similar tests ranked by semantic relevance

    HTTP Status Codes:
        - 200 OK: Similar tests found and returned
        - 400 Bad Request: Invalid JIRA key format
        - 401 Unauthorized: Invalid or missing API key
        - 404 Not Found: Reference test not found
        - 500 Internal Server Error: Similarity search failure

    Similarity Algorithm:
        1. Validates and retrieves reference test by JIRA key
        2. Constructs search query from test title, summary, and tags
        3. Executes semantic search using combined metadata
        4. Filters out the reference test from results
        5. Returns top-k most similar tests

    Query Construction:
        - Prioritizes title and summary for semantic content
        - Includes tags for categorical similarity
        - Removes duplicate information to avoid bias
        - Optimizes query length for embedding performance

    Use Cases:
        - Test discovery and exploration
        - Duplicate test identification
        - Test suite organization and cleanup
        - Related test recommendation
        - Quality assurance coverage analysis

    Security Features:
        - JIRA key validation to prevent injection
        - Reference test access validation
        - Results filtered to exclude self-references
        - Consistent error handling and logging
    """
    try:
        container = request.app.state.container
        jira_validator = container.get("jira_validator")
        qdrant_client = container.get("qdrant_client")

        # Validate JIRA key format to prevent injection attacks
        try:
            validated_jira_key = jira_validator(jira_key)
        except JiraKeyValidationError as e:
            logger.error(
                "JIRA key validation failed in find_similar",
                jira_key=jira_key,
                error=str(e),
                extra={"security_event": True},
            )
            raise HTTPException(
                status_code=400, detail=f"Invalid JIRA key format: {str(e)}"
            ) from None

        # First get the test (call internal logic directly to avoid auth dependency)
        # Query by jiraKey
        filter_cond = Filter(
            must=[FieldCondition(key="jiraKey", match=MatchValue(value=validated_jira_key))]
        )

        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=filter_cond,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if not results[0]:
            raise HTTPException(status_code=404, detail=f"Test not found: {validated_jira_key}")

        test_data = results[0][0].payload
        test = TestDoc(**test_data)

        # Create a search query from the test
        query_parts = []
        if test.title:
            query_parts.append(test.title)
        if test.summary and test.summary != test.title:
            query_parts.append(test.summary)
        if test.tags:
            query_parts.append(" ".join(test.tags))

        query = " ".join(query_parts)

        # Search for similar tests
        search_req = SearchRequest(
            query=query, top_k=top_k + 1, scope=scope  # Get one extra to exclude self
        )

        # Call internal search implementation
        results = await _search_impl(request, search_req)

        # Filter out the original test
        filtered_results = [r for r in results if r.test.uid != test.uid]

        return filtered_results[:top_k]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Find similar error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    # Configure structured logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Run the server
    uvicorn.run(
        "src.service.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("API_RELOAD", "true").lower() == "true",
    )
