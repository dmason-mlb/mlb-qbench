"""FastAPI service for MLB QBench with PostgreSQL + pgvector backend.

This module implements the REST API for the MLB QBench test retrieval system
using PostgreSQL with pgvector for semantic search capabilities.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from ..auth import require_api_key
from ..db import PostgresVectorDB
from ..embedder import get_embedder, prepare_text_for_embedding
from ..models.test_models import (
    IngestRequest,
    IngestResponse,
    SearchRequest,
    SearchResult,
    TestDoc,
)

# Load environment variables
load_dotenv()

# Configure logging
logger = structlog.get_logger()

# Global instances
db: Optional[PostgresVectorDB] = None
embedder = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle - startup and shutdown."""
    global db, embedder

    logger.info("Starting MLB QBench API with PostgreSQL backend")

    # Initialize database
    db = PostgresVectorDB()
    await db.initialize()
    logger.info("PostgreSQL connection pool initialized")

    # Initialize embedder
    embedder = get_embedder()
    logger.info(
        "Embedder initialized",
        provider=os.getenv("EMBED_PROVIDER", "openai"),
        model=os.getenv("EMBED_MODEL", "text-embedding-3-large"),
    )

    # Get initial statistics
    stats = await db.get_statistics()
    logger.info(
        "Database statistics",
        total_documents=stats.get("total_documents", 0),
        total_steps=stats.get("total_steps", 0),
    )

    yield

    # Cleanup on shutdown
    logger.info("Shutting down MLB QBench API")
    if db:
        await db.close()


# Create FastAPI app
app = FastAPI(
    title="MLB QBench API",
    description="Test retrieval service using PostgreSQL with pgvector",
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/healthz")
async def health_check():
    """Health check endpoint for container orchestration."""
    try:
        # Check database connection
        stats = await db.get_statistics()

        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": {
                "connected": True,
                "total_documents": stats.get("total_documents", 0),
                "total_steps": stats.get("total_steps", 0),
            },
            "embedder": {
                "provider": os.getenv("EMBED_PROVIDER", "openai"),
                "model": os.getenv("EMBED_MODEL", "text-embedding-3-large"),
            },
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy") from e


@app.get("/metrics")
async def get_metrics():
    """Get service metrics and statistics."""
    try:
        stats = await db.get_statistics()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": stats,
            "embedder": {
                "provider": os.getenv("EMBED_PROVIDER", "openai"),
                "model": os.getenv("EMBED_MODEL", "text-embedding-3-large"),
                "embed_count": embedder.embed_count if embedder else 0,
                "total_tokens": embedder.total_tokens if embedder else 0,
            },
        }
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics") from e


@app.post("/search", response_model=SearchResult)
@limiter.limit("60/minute")
async def search_tests(
    request: Request, search_request: SearchRequest, api_key: str = Security(require_api_key)
) -> SearchResult:
    """Search for tests using semantic similarity.

    Args:
        request: FastAPI request object (for rate limiting)
        search_request: Search query and filters
        api_key: API key for authentication

    Returns:
        SearchResult with matching tests and metadata
    """
    try:
        # Prepare and embed query
        prepared_query = prepare_text_for_embedding(search_request.query)
        query_embedding = await embedder.embed(prepared_query)

        # Build filters from request
        filters = {}
        if search_request.filters:
            if search_request.filters.priority:
                filters["priority"] = search_request.filters.priority
            if search_request.filters.tags:
                filters["tags"] = search_request.filters.tags
            if search_request.filters.platforms:
                filters["platforms"] = search_request.filters.platforms
            if search_request.filters.folderStructure:
                filters["folderStructure"] = search_request.filters.folderStructure
            if search_request.filters.testType:
                filters["testType"] = search_request.filters.testType

        # Perform hybrid search
        results = await db.hybrid_search(
            query_embedding=query_embedding,
            filters=filters,
            limit=search_request.limit or 10,
            include_steps=True,
        )

        # Format results
        test_results = []
        for result in results:
            test_doc = TestDoc(
                uid=result["uid"],
                testCaseId=result["test_case_id"],
                jiraKey=result.get("jira_key"),
                title=result["title"],
                description=result.get("description"),
                summary=result.get("summary"),
                priority=result.get("priority"),
                tags=result.get("tags", []),
                platforms=result.get("platforms", []),
                folderStructure=result.get("folder_structure"),
                testType=result.get("test_type"),
                steps=[],  # Steps included separately if needed
                source="PostgreSQL",
            )

            test_results.append(
                {
                    "test": test_doc,
                    "similarity": result["similarity"],
                    "matched_steps": result.get("matched_steps", []),
                }
            )

        return SearchResult(
            query=search_request.query,
            results=test_results,
            total=len(test_results),
            filters_applied=search_request.filters.model_dump() if search_request.filters else {},
        )

    except Exception as e:
        logger.error("Search failed", error=str(e), query=search_request.query)
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}") from e


@app.get("/by-jira/{jira_key}")
@limiter.limit("60/minute")
async def get_test_by_jira(
    request: Request, jira_key: str, api_key: str = Security(require_api_key)
) -> dict[str, Any]:
    """Get a test by its JIRA key.

    Args:
        request: FastAPI request object (for rate limiting)
        jira_key: JIRA issue key
        api_key: API key for authentication

    Returns:
        Test document if found
    """
    try:
        result = await db.search_by_jira_key(jira_key)

        if not result:
            raise HTTPException(status_code=404, detail=f"Test with JIRA key {jira_key} not found")

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get test by JIRA key", error=str(e), jira_key=jira_key)
        raise HTTPException(status_code=500, detail="Failed to retrieve test") from e


@app.get("/similar/{uid}")
@limiter.limit("60/minute")
async def find_similar_tests(
    request: Request,
    uid: str,
    limit: int = Query(10, ge=1, le=50),
    api_key: str = Security(require_api_key),
) -> list[dict[str, Any]]:
    """Find tests similar to a given test.

    Args:
        request: FastAPI request object (for rate limiting)
        uid: Test UID
        limit: Maximum number of similar tests
        api_key: API key for authentication

    Returns:
        List of similar tests
    """
    try:
        results = await db.find_similar_tests(uid, limit)

        if not results:
            raise HTTPException(status_code=404, detail=f"Test with UID {uid} not found")

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to find similar tests", error=str(e), uid=uid)
        raise HTTPException(status_code=500, detail="Failed to find similar tests") from e


@app.post("/ingest", response_model=IngestResponse)
@limiter.limit("5/minute")
async def ingest_tests(
    request: Request, ingest_request: IngestRequest, api_key: str = Security(require_api_key)
) -> IngestResponse:
    """Ingest test data into the database.

    Args:
        request: FastAPI request object (for rate limiting)
        ingest_request: Test data to ingest
        api_key: API key for authentication

    Returns:
        Ingestion statistics
    """
    try:
        # Convert request to TestDoc objects
        test_docs = []
        for test_data in ingest_request.tests:
            # Create TestDoc from raw data
            test_doc = TestDoc(**test_data)
            test_docs.append(test_doc)

        # Batch insert with embeddings
        result = await db.batch_insert_documents(
            documents=test_docs, embedder=embedder, batch_size=ingest_request.batch_size or 100
        )

        return IngestResponse(
            status="success" if result["failed"] == 0 else "partial",
            total_processed=result["total"],
            successful=result["inserted"],
            failed=result["failed"],
            errors=result.get("errors", []),
        )

    except Exception as e:
        logger.error("Ingestion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}") from e


@app.delete("/tests/{uid}")
@limiter.limit("10/minute")
async def delete_test(
    request: Request, uid: str, api_key: str = Security(require_api_key)
) -> dict[str, str]:
    """Delete a test by UID.

    Args:
        request: FastAPI request object (for rate limiting)
        uid: Test UID
        api_key: API key for authentication

    Returns:
        Deletion confirmation
    """
    try:
        deleted = await db.delete_by_uid(uid)

        if not deleted:
            raise HTTPException(status_code=404, detail=f"Test with UID {uid} not found")

        return {"status": "deleted", "uid": uid}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete test", error=str(e), uid=uid)
        raise HTTPException(status_code=500, detail="Failed to delete test") from e


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "MLB QBench API",
        "version": "2.0.0",
        "backend": "PostgreSQL + pgvector",
        "endpoints": {
            "search": "POST /search",
            "get_by_jira": "GET /by-jira/{jira_key}",
            "find_similar": "GET /similar/{uid}",
            "ingest": "POST /ingest",
            "delete": "DELETE /tests/{uid}",
            "health": "GET /healthz",
            "metrics": "GET /metrics",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
