# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MLB QBench is a test retrieval service that uses PostgreSQL with pgvector extension to provide semantic search over test cases. The system ingests test data from multiple sources including TestRail SQLite databases (104k+ tests), normalizes fields across different formats, and exposes a FastAPI interface for AI-powered test discovery. The system uses OpenAI text-embedding-3-small (1536 dimensions) for cost-effective embeddings that work with pgvector's HNSW indexes.

## Key Development Commands

```bash
# Setup and Installation
pip install -e .                     # Install project in editable mode
pip install -e ".[dev]"             # Install with dev dependencies

# PostgreSQL/Services
make postgres-setup                 # Set up PostgreSQL with pgvector extension
make postgres-schema                # Create PostgreSQL schema and indexes
make migrate-optimized              # Run optimized migration (104k tests)
make migrate-test                   # Test migration with 100 records
make dev                            # Start API server with PostgreSQL
make stop                           # Stop all services
make clean                          # Stop services and clean all data

# Development Server
make api-dev                        # Start FastAPI server (port 8000)
cd src/service && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Data Operations
make migrate-optimized              # Migrate all 104k tests from TestRail
make migrate-test                   # Test migration with 100 records
make migrate-resume-optimized      # Resume interrupted migration
python scripts/migrate_optimized.py --batch-size 500 --checkpoint-interval 5000

# MCP Integration
make mcp-server                     # Start MCP server for AI tool integration

# Code Quality
make lint                           # Run ruff and mypy
make format                         # Format with black and ruff
ruff check src/ tests/             # Run linter only
mypy src/                          # Run type checker only

# Testing
make test                          # Run full test suite with coverage
pytest tests/ -v                   # Run tests verbose
pytest tests/test_specific.py -k "test_name"  # Run specific test

# Environment
make check-env                     # Verify environment variables
```

## High-Level Architecture

### Dual Table Design
The system uses two PostgreSQL tables with pgvector for different search granularities:

1. **test_documents**: Document-level embeddings
   - One vector(1536) per test case containing title + description
   - Stores all test metadata from TestRail (jiraKey, priority, tags, platforms, etc.)
   - HNSW index for fast similarity search (100-1000x faster than sequential)
   - Preserves TestRail IDs (test_case_id, suite_id, section_id, project_id)

2. **test_steps**: Step-level embeddings  
   - One vector(1536) per test step containing action + expected result
   - Links to parent document via foreign key to test_documents
   - Separate HNSW index for step-level similarity search
   - Enables finding tests by specific actions or validations

### Async Provider-Agnostic Embedding System
The `embedder.py` module implements a fully async factory pattern:
- Base `EmbeddingProvider` class defines async interface with `async def embed()`
- Async implementations for OpenAI, Cohere, Vertex AI, Azure
- Provider selected via `EMBED_PROVIDER` environment variable
- Concurrent batch processing with configurable batch sizes (default: 25 texts/batch)
- Automatic retry logic with exponential backoff using `AsyncRetrying`
- Resource management with proper async client cleanup
- **Performance**: 25x fewer API calls through intelligent batching

### Async Data Ingestion Pipeline
Two async ingestion modules handle different test formats:
- `ingest_functional.py`: Processes Xray functional tests with async batch operations
- `ingest_api.py`: Processes API test format with concurrent embedding generation
- Both normalize to common schema defined in `test_models.py`
- Key mappings: `labels` → `tags`, `folder` → `folderStructure`
- **Batch Processing**: `create_points_from_test_batch()` functions process multiple tests concurrently
- **Performance**: Dramatically reduced ingestion time through async batch embedding

### Async Hybrid Search Algorithm
The search endpoint (`/search`) implements high-performance async search:
1. Asynchronously embeds user query using configured provider
2. Concurrently searches both collections using `asyncio.gather()`
3. Applies filters to both result sets in parallel
4. Merges results with configurable weights (0.7 doc, 0.3 step)
5. Reranks by combined scores
6. Returns top-k results with matched steps included
7. **Performance**: ~50% faster than sequential search for full-scope queries

### API Endpoints with Async Rate Limiting
- `POST /search`: Async semantic search with concurrent processing (rate limited: 60/minute)
- `POST /ingest`: Async batch ingestion with concurrent embedding (rate limited: 5/minute)
- `GET /by-jira/{key}`: Direct lookup by JIRA key with validation
- `GET /similar/{uid}`: Find similar tests using async search
- `GET /healthz`: Service and collection health monitoring
- `GET /metrics`: Resource usage and performance metrics (NEW)

### Async Architecture & Performance
The system implements a fully async architecture for maximum performance:

**Core Async Components:**
- **Embedding Providers**: All providers (OpenAI, Cohere, Vertex, Azure) use async clients
- **Search Operations**: Concurrent document and step searches using `asyncio.gather()`
- **Batch Processing**: Intelligent batching for embedding API calls (25 texts/batch)
- **Rate Limiting**: Async-compatible rate limiting with slowapi integration
- **Resource Management**: Proper async cleanup and resource disposal

**Performance Benefits:**
- Search latency reduced by ~50% through concurrent operations
- Ingestion throughput improved by 25x through batch processing
- Memory efficient async resource management
- Rate limiting prevents API abuse and ensures fair usage

**Monitoring & Metrics:**
- `/metrics` endpoint provides real-time performance statistics
- Embedding provider usage tracking (request counts, token usage)
- Dependency injection container status monitoring
- Rate limiter activity tracking

### MCP Server Integration
The project includes an MCP (Model Context Protocol) server for AI tool integration:
- Located in `src/mcp/server.py`
- Exposes search and ingestion capabilities as tools
- Configured via `mcp.json` for Claude Desktop integration
- Start with `make mcp-server` or `python -m src.mcp`

## Environment Configuration

Required environment variables:
```bash
# PostgreSQL Configuration
DATABASE_URL=postgresql://username@localhost/mlb_qbench

# Embedding Provider (Optimized for OpenAI)
EMBED_PROVIDER=openai               # Currently optimized for OpenAI
EMBED_MODEL=text-embedding-3-small  # 1536 dimensions for pgvector compatibility
# Cost: ~$0.02 per 1M tokens (5x cheaper than text-embedding-3-large)

# OpenAI API Key (Required)
OPENAI_API_KEY=your-key

# API Authentication (optional)
MASTER_API_KEY=your-master-key      # Admin access for all operations
API_KEYS=key1,key2,key3            # Comma-separated list of valid API keys
```

## Key Technical Decisions

### Idempotent Ingestion
- Always check if UID exists before inserting
- Delete existing document and its steps before re-ingestion
- Ensures consistency when re-running ingestion

### pgvector HNSW Index Configuration
- `m=16, ef_construct=64` optimized for 100k+ documents
- Vector dimensions: 1536 (text-embedding-3-small)
- Indexes on all filterable fields for performance
- 100-1000x faster than sequential scan with indexes

### Batch Processing
- Embeddings: 100 texts per batch (configurable)
- Ingestion: 50 documents per batch
- Prevents rate limits and memory issues

### Error Handling
- Tenacity retry logic on embedding calls
- Graceful handling of missing fields during normalization
- Detailed logging with structlog for debugging

### API Security
- Optional API key authentication system in `src/auth/`
- Master key for admin operations, multiple user keys supported
- Rate limiting with slowapi integration
- Secure key validation and request filtering

## Common Development Tasks

### Adding a New Embedding Provider
1. Create new class in `embedder.py` inheriting from `EmbeddingProvider`
2. Implement `_embed_batch()` method
3. Add to factory function `get_embedder()`
4. Add required environment variables

### Modifying the Test Schema
1. Update Pydantic models in `test_models.py`
2. Update normalization logic in `ingest/normalize.py`
3. Modify collection creation in `models/schema.py` if adding indexes
4. Update ingestion modules to handle new fields

### Debugging Search Results
1. Check embedding dimensions match collection config (3072 for OpenAI)
2. Verify filters are properly constructed in `build_filter()`
3. Use `/similar` endpoint to test pure vector similarity
4. Check logs for query embedding and search parameters

## Performance Considerations

- Full migration of 104k tests takes ~35 minutes at 50 docs/second
- Search latency <100ms with HNSW indexes
- Embedding costs: ~$1.04 for 104k tests with text-embedding-3-small
- PostgreSQL database size: ~2GB for 104k documents with vectors and indexes
- Connection pooling with 20-50 async connections for high throughput

## Troubleshooting Tips

### Docker Permission Issues
If you get "permission denied" errors:
```bash
rm -rf qdrant_storage && mkdir qdrant_storage
make qdrant-up
```

### Module Import Errors
Ensure you installed in editable mode:
```bash
pip install -e .
```

### PostgreSQL Connection Failed
1. Check if PostgreSQL is running: `pg_isready`
2. Verify database exists: `psql -l | grep mlb_qbench`
3. Check pgvector installation: `psql -d mlb_qbench -c "SELECT * FROM pg_extension WHERE extname = 'vector';"`
4. Verify schema: `psql -d mlb_qbench -c "\dt"` should show test_documents, test_steps tables