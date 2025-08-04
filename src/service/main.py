"""FastAPI service for test retrieval."""

import os
from typing import List, Optional, Dict, Any, Literal
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Depends, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import structlog
from dotenv import load_dotenv
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny, MatchText
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ..models.schema import get_client, TEST_DOCS_COLLECTION, TEST_STEPS_COLLECTION, check_collections_health
from ..models.test_models import SearchRequest, SearchResult, IngestRequest, IngestResponse, TestDoc
from ..embedder import get_embedder, prepare_text_for_embedding
from ..ingest.ingest_functional import ingest_functional_tests
from ..ingest.ingest_api import ingest_api_tests
from ..auth import require_api_key
from ..auth.auth import get_api_key
from ..security import validate_data_file_path, PathValidationError

# Load environment variables
load_dotenv()

# Configure logging
logger = structlog.get_logger()

# Initialize clients
qdrant_client = None
embedder = None

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize clients on startup."""
    global qdrant_client, embedder
    
    logger.info("Initializing clients...")
    qdrant_client = get_client()
    embedder = get_embedder()
    
    # Check collections health
    health = check_collections_health(qdrant_client)
    logger.info("Collections health", health=health)
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="MLB QBench Test Retrieval API",
    version="1.0.0",
    description="Semantic search API for test retrieval from Qdrant",
    lifespan=lifespan
)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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


async def search_documents(query: str, top_k: int, filters: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Search test documents."""
    query_embedding = embedder.embed(prepare_text_for_embedding(query))
    
    results = qdrant_client.search(
        collection_name=TEST_DOCS_COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        query_filter=build_filter(filters),
        with_payload=True,
        with_vectors=False
    )
    
    return [(r.payload, r.score) for r in results]


async def search_steps(query: str, top_k: int, filters: Optional[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Search test steps and group by parent."""
    query_embedding = embedder.embed(prepare_text_for_embedding(query))
    
    # Search steps
    step_results = qdrant_client.search(
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
        scroll_result = qdrant_client.scroll(
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
    top_k: int
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
    for uid, step_matches in steps_by_parent.items():
        if uid not in doc_map:
            # Fetch the document
            doc_filter = Filter(
                must=[FieldCondition(key="uid", match=MatchValue(value=uid))]
            )
            docs = qdrant_client.scroll(
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
async def health(api_key: str = Security(get_api_key)):
    """Health check endpoint - requires API key authentication."""
    try:
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


@app.post("/search", response_model=List[SearchResult])
@limiter.limit("60/minute")
async def search(request: Request, search_request: SearchRequest, api_key: str = require_api_key):
    """
    Search for tests using semantic search.
    
    Searches both document-level and step-level vectors,
    merges results, and returns top-k matches.
    """
    try:
        # Search documents
        if search_request.scope in ["all", "docs"]:
            doc_results = await search_documents(
                search_request.query,
                search_request.top_k,
                search_request.filters
            )
        else:
            doc_results = []
        
        # Search steps
        if search_request.scope in ["all", "steps"]:
            steps_by_parent = await search_steps(
                search_request.query,
                search_request.top_k,
                search_request.filters
            )
        else:
            steps_by_parent = {}
        
        # Merge and rerank
        results = await merge_and_rerank_results(
            doc_results,
            steps_by_parent,
            search_request.top_k
        )
        
        logger.info(
            "Search completed",
            query=search_request.query,
            results_count=len(results),
            scope=search_request.scope
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest", response_model=IngestResponse)
@limiter.limit("5/minute")
async def ingest(request: Request, ingest_request: IngestRequest, api_key: str = require_api_key):
    """
    Ingest test data from JSON files.
    
    Can ingest functional tests, API tests, or both.
    """
    try:
        response = IngestResponse()
        
        # Ingest functional tests if path provided
        if ingest_request.functional_path:
            try:
                # Secure path validation to prevent SSRF and directory traversal
                functional_path = validate_data_file_path(ingest_request.functional_path)
                
                if not functional_path.exists():
                    raise HTTPException(status_code=404, detail=f"Functional file not found: {ingest_request.functional_path}")
                
                result = ingest_functional_tests(str(functional_path))
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
                api_path = validate_data_file_path(ingest_request.api_path)
                
                if not api_path.exists():
                    raise HTTPException(status_code=404, detail=f"API file not found: {ingest_request.api_path}")
                
                result = ingest_api_tests(str(api_path))
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
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/by-jira/{jira_key}", response_model=TestDoc)
async def get_by_jira(jira_key: str, api_key: str = require_api_key):
    """Get a test by its JIRA key."""
    try:
        # Query by jiraKey
        filter_cond = Filter(
            must=[FieldCondition(key="jiraKey", match=MatchValue(value=jira_key))]
        )
        
        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=filter_cond,
            limit=1,
            with_payload=True,
            with_vectors=False
        )
        
        if not results[0]:
            raise HTTPException(status_code=404, detail=f"Test not found: {jira_key}")
        
        test_data = results[0][0].payload
        return TestDoc(**test_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get by JIRA error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/similar/{jira_key}")
async def find_similar(
    jira_key: str,
    scope: Literal["docs", "steps", "all"] = Query("docs", description="Search scope"),
    top_k: int = Query(10, ge=1, le=100, description="Number of results"),
    api_key: str = require_api_key
):
    """Find tests similar to a given test."""
    try:
        # First get the test (call internal logic directly to avoid auth dependency)
        # Query by jiraKey
        filter_cond = Filter(
            must=[FieldCondition(key="jiraKey", match=MatchValue(value=jira_key))]
        )
        
        results = qdrant_client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            scroll_filter=filter_cond,
            limit=1,
            with_payload=True,
            with_vectors=False
        )
        
        if not results[0]:
            raise HTTPException(status_code=404, detail=f"Test not found: {jira_key}")
        
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
        
        results = await search(search_req)
        
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