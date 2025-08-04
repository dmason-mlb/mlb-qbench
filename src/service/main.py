"""FastAPI service for test retrieval."""

import asyncio
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client.models import FieldCondition, Filter, MatchAny, MatchText, MatchValue
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

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
from ..models.test_models import IngestRequest, IngestResponse, SearchRequest, SearchResult, TestDoc
from ..security import JiraKeyValidationError, PathValidationError

# Load environment variables
load_dotenv()

# Configure logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services using dependency injection."""
    # Configure services in the container
    container = configure_services()

    logger.info("Initializing services...")

    # Initialize core services
    qdrant_client = container.get('qdrant_client')
    embedder = container.get('embedder')

    # Check collections health
    health = check_collections_health(qdrant_client)
    logger.info("Collections health", health=health)

    # Store container in app state for access in endpoints
    app.state.container = container

    # Set up rate limiter for exception handling
    limiter = container.get('rate_limiter')
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Create decorator functions for rate limiting
    search_limiter = limiter.limit("60/minute")
    ingest_limiter = limiter.limit("5/minute")
    app.state.search_limiter = search_limiter
    app.state.ingest_limiter = ingest_limiter

    yield

    # Cleanup
    logger.info("Shutting down services...")
    await container.dispose_async()


# Create FastAPI app
app = FastAPI(
    title="MLB QBench Test Retrieval API",
    version="1.0.0",
    description="Semantic search API for test retrieval from Qdrant",
    lifespan=lifespan
)

# Rate limiter will be initialized in lifespan and stored in app.state.container

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


def build_filter(filters: Optional[Dict[str, Any]]) -> Optional[Filter]:
    """
    Build Qdrant filter from request filters with security validation.
    
    Args:
        filters: Dictionary of filter conditions (will be validated)
        
    Returns:
        Qdrant Filter object or None if no valid filters
        
    Raises:
        ValueError: If filter validation fails
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
                    FieldCondition(
                        key=actual_field,
                        match=MatchText(text=str(value))
                    )
                )
            elif isinstance(value, list):
                # Array fields (tags, platforms, etc.) or IN operations
                if value:  # Only add if list is not empty
                    conditions.append(
                        FieldCondition(
                            key=field,
                            match=MatchAny(any=value)
                        )
                    )
            else:
                # Single value fields
                conditions.append(
                    FieldCondition(
                        key=field,
                        match=MatchValue(value=value)
                    )
                )

        if conditions:
            return Filter(must=conditions)

        return None

    except Exception as e:
        # Log the security violation attempt
        logger.error(
            "Filter validation failed - potential security threat",
            error=str(e),
            filters=filters,
            extra={"security_event": True}
        )
        # Re-raise as ValueError with generic message to avoid info disclosure
        raise ValueError("Invalid filter parameters") from None


async def search_documents(query: str, top_k: int, filters: Optional[Dict[str, Any]], container: Container) -> List[Dict[str, Any]]:
    """Search test documents."""
    embedder = container.get('embedder')
    qdrant_client = container.get('qdrant_client')

    query_embedding = await embedder.embed(prepare_text_for_embedding(query))

    results = await asyncio.to_thread(
        qdrant_client.search,
        collection_name=TEST_DOCS_COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=build_filter(filters),
        with_payload=True,
        with_vectors=False
    )

    return [(r.payload, r.score) for r in results]


async def search_steps(query: str, top_k: int, filters: Optional[Dict[str, Any]], container: Container) -> Dict[str, List[Dict[str, Any]]]:
    """Search test steps and group by parent."""
    embedder = container.get('embedder')
    qdrant_client = container.get('qdrant_client')

    query_embedding = await embedder.embed(prepare_text_for_embedding(query))

    # Search steps
    step_results = await asyncio.to_thread(
        qdrant_client.search,
        collection_name=TEST_STEPS_COLLECTION,
        query_vector=query_embedding,
        limit=top_k * 3,  # Get more steps since we'll group by parent
        with_payload=True,
        with_vectors=False
    )

    # Group steps by parent_uid
    steps_by_parent = {}
    for result in step_results:
        parent_uid = result.payload.get("parent_uid")
        if parent_uid not in steps_by_parent:
            steps_by_parent[parent_uid] = []
        steps_by_parent[parent_uid].append({
            "step_index": result.payload.get("step_index"),
            "action": result.payload.get("action"),
            "expected": result.payload.get("expected", []),
            "score": result.score
        })

    # If we have filters, we need to fetch parent docs to apply filters
    if filters and steps_by_parent:
        # Get parent documents
        parent_uids = list(steps_by_parent.keys())
        parent_filter = Filter(
            must=[
                FieldCondition(
                    key="uid",
                    match=MatchAny(any=parent_uids)
                )
            ]
        )

        # Combine with user filters
        if build_filter(filters):
            parent_filter.must.extend(build_filter(filters).must)

        # Query parent docs
        scroll_result = await asyncio.to_thread(
            qdrant_client.scroll,
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=parent_filter,
            limit=len(parent_uids),
            with_payload=["uid"],
            with_vectors=False
        )

        # Keep only steps whose parents pass the filter
        valid_parent_uids = {point.payload["uid"] for point in scroll_result[0]}
        steps_by_parent = {
            uid: steps for uid, steps in steps_by_parent.items()
            if uid in valid_parent_uids
        }

    return steps_by_parent


async def merge_and_rerank_results(
    doc_results: List[tuple[Dict[str, Any], float]],
    steps_by_parent: Dict[str, List[Dict[str, Any]]],
    top_k: int,
    container: Container
) -> List[SearchResult]:
    """Merge document and step search results."""
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
            matched_steps=[s["step_index"] for s in step_matches]
        )
        all_results.append(result)

    # Add documents that only have step matches (not in doc results)
    qdrant_client = container.get('qdrant_client')
    for uid, step_matches in steps_by_parent.items():
        if uid not in doc_map:
            # Fetch the document
            doc_filter = Filter(
                must=[FieldCondition(key="uid", match=MatchValue(value=uid))]
            )
            docs = await asyncio.to_thread(
                qdrant_client.scroll,
                collection_name=TEST_DOCS_COLLECTION,
                scroll_filter=doc_filter,
                limit=1,
                with_payload=True,
                with_vectors=False
            )

            if docs[0]:
                doc = docs[0][0].payload
                max_step_score = max(s["score"] for s in step_matches)

                test_doc = TestDoc(**doc)
                result = SearchResult(
                    test=test_doc,
                    score=max_step_score * 0.8,  # Slightly lower score for step-only matches
                    matched_steps=[s["step_index"] for s in step_matches]
                )
                all_results.append(result)

    # Sort by score and return top-k
    all_results.sort(key=lambda x: x.score, reverse=True)
    return all_results[:top_k]


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "MLB QBench Test Retrieval API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/healthz")
async def health(request: Request, api_key: str = Security(get_api_key)):
    """Health check endpoint - requires API key authentication."""
    try:
        container = request.app.state.container
        qdrant_client = container.get('qdrant_client')
        health_status = check_collections_health(qdrant_client)

        # Log health check access for security audit
        logger.info(
            "Health check accessed",
            api_key_prefix=api_key[:8] + "..." if len(api_key) > 8 else "***",
            health_status=health_status["status"]
        )

        return {
            "status": "healthy" if health_status["status"] == "healthy" else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "qdrant": health_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


@app.get("/metrics")
async def metrics(request: Request, api_key: str = Security(get_api_key)):
    """Resource usage and performance metrics endpoint."""
    try:
        container = request.app.state.container
        
        # Get embedding provider stats
        embedder = container.get('embedder')
        embedder_stats = embedder.get_stats()
        
        # Get container stats
        container_stats = container.get_service_info()
        
        # Get rate limiter stats (if available)
        limiter = request.app.state.limiter
        limiter_stats = {}
        if hasattr(limiter, '_storage'):
            limiter_stats = {
                "storage_type": type(limiter._storage).__name__,
                "active_limits": len(getattr(limiter._storage, '_storage', {}))
            }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "embedding_provider": embedder_stats,
            "dependency_container": container_stats,
            "rate_limiter": limiter_stats,
            "async_framework": {
                "concurrent_searches_enabled": True,
                "batch_processing_enabled": True,
                "resource_management": "async"
            }
        }
    except Exception as e:
        logger.error(f"Metrics collection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _search_impl(request: Request, search_request: SearchRequest) -> List[SearchResult]:
    """Internal search implementation with concurrent processing."""
    import asyncio
    
    container = request.app.state.container

    # Prepare concurrent search tasks
    tasks = []
    
    # Add document search task if needed
    if search_request.scope in ["all", "docs"]:
        doc_task = search_documents(
            search_request.query,
            search_request.top_k,
            search_request.filters,
            container
        )
        tasks.append(("docs", doc_task))
    
    # Add step search task if needed  
    if search_request.scope in ["all", "steps"]:
        steps_task = search_steps(
            search_request.query,
            search_request.top_k,
            search_request.filters,
            container
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
        doc_results,
        steps_by_parent,
        search_request.top_k,
        container
    )

    logger.info(
        "Search completed",
        query=search_request.query,
        results_count=len(results),
        scope=search_request.scope,
        concurrent_searches=len(tasks)
    )

    return results

@app.post("/search", response_model=List[SearchResult])
async def search(request: Request, search_request: SearchRequest, api_key: str = require_api_key):
    """
    Search for tests using semantic search.
    
    Searches both document-level and step-level vectors,
    merges results, and returns top-k matches.
    """
    try:
        # Apply rate limiting directly
        limiter = request.app.state.limiter
        try:
            await limiter.limit("60/minute")(request)
        except RateLimitExceeded:
            logger.warning(f"Rate limit exceeded for search request from {request.client.host}")
            raise
        
        return await _search_impl(request, search_request)
    except RateLimitExceeded:
        raise  # Re-raise rate limit exceptions
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: Request, ingest_request: IngestRequest, api_key: str = require_api_key):
    """
    Ingest test data from JSON files.
    
    Can ingest functional tests, API tests, or both.
    """
    try:
        # Apply rate limiting directly
        limiter = request.app.state.limiter
        try:
            await limiter.limit("5/minute")(request)
        except RateLimitExceeded:
            logger.warning(f"Rate limit exceeded for ingest request from {request.client.host}")
            raise
        
        container = request.app.state.container
        path_validator = container.get('path_validator')
        response = IngestResponse()

        # Ingest functional tests if path provided
        if ingest_request.functional_path:
            try:
                # Secure path validation to prevent SSRF and directory traversal
                functional_path = path_validator(ingest_request.functional_path)

                if not functional_path.exists():
                    raise HTTPException(status_code=404, detail=f"Functional file not found: {ingest_request.functional_path}")

                result = await ingest_functional_tests(str(functional_path))
                response.functional_ingested = result.get("ingested", 0)
                response.errors.extend(result.get("errors", []))
                response.warnings.extend(result.get("warnings", []))

            except PathValidationError as e:
                logger.error(
                    "Functional path validation failed",
                    path=ingest_request.functional_path,
                    error=str(e),
                    extra={"security_event": True}
                )
                raise HTTPException(status_code=400, detail=f"Invalid functional file path: {str(e)}")

        # Ingest API tests if path provided
        if ingest_request.api_path:
            try:
                # Secure path validation to prevent SSRF and directory traversal
                api_path = path_validator(ingest_request.api_path)

                if not api_path.exists():
                    raise HTTPException(status_code=404, detail=f"API file not found: {ingest_request.api_path}")

                result = await ingest_api_tests(str(api_path))
                response.api_ingested = result.get("ingested", 0)
                response.errors.extend(result.get("errors", []))
                response.warnings.extend(result.get("warnings", []))

            except PathValidationError as e:
                logger.error(
                    "API path validation failed",
                    path=ingest_request.api_path,
                    error=str(e),
                    extra={"security_event": True}
                )
                raise HTTPException(status_code=400, detail=f"Invalid API file path: {str(e)}")

        logger.info(
            "Ingestion completed",
            functional=response.functional_ingested,
            api=response.api_ingested,
            errors=len(response.errors)
        )

        return response

    except RateLimitExceeded:
        raise  # Re-raise rate limit exceptions
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/by-jira/{jira_key}", response_model=TestDoc)
async def get_by_jira(request: Request, jira_key: str, api_key: str = require_api_key):
    """Get a test by its JIRA key."""
    try:
        container = request.app.state.container
        jira_validator = container.get('jira_validator')
        qdrant_client = container.get('qdrant_client')

        # Validate JIRA key format to prevent injection attacks
        try:
            validated_jira_key = jira_validator(jira_key)
        except JiraKeyValidationError as e:
            logger.error(
                "JIRA key validation failed in get_by_jira",
                jira_key=jira_key,
                error=str(e),
                extra={"security_event": True}
            )
            raise HTTPException(status_code=400, detail=f"Invalid JIRA key format: {str(e)}")

        # Query by jiraKey
        filter_cond = Filter(
            must=[FieldCondition(key="jiraKey", match=MatchValue(value=validated_jira_key))]
        )

        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=filter_cond,
            limit=1,
            with_payload=True,
            with_vectors=False
        )

        if not results[0]:
            raise HTTPException(status_code=404, detail=f"Test not found: {validated_jira_key}")

        test_data = results[0][0].payload
        return TestDoc(**test_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get by JIRA error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/similar/{jira_key}")
async def find_similar(
    request: Request,
    jira_key: str,
    scope: Literal["docs", "steps", "all"] = Query("docs", description="Search scope"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results"),
    api_key: str = require_api_key
):
    """Find tests similar to a given test."""
    try:
        container = request.app.state.container
        jira_validator = container.get('jira_validator')
        qdrant_client = container.get('qdrant_client')

        # Validate JIRA key format to prevent injection attacks
        try:
            validated_jira_key = jira_validator(jira_key)
        except JiraKeyValidationError as e:
            logger.error(
                "JIRA key validation failed in find_similar",
                jira_key=jira_key,
                error=str(e),
                extra={"security_event": True}
            )
            raise HTTPException(status_code=400, detail=f"Invalid JIRA key format: {str(e)}")

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
            with_vectors=False
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
            query=query,
            top_k=top_k + 1,  # Get one extra to exclude self
            scope=scope
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
        raise HTTPException(status_code=500, detail=str(e))


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
            structlog.dev.ConsoleRenderer()
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
        reload=os.getenv("API_RELOAD", "true").lower() == "true"
    )
