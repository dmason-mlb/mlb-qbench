# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MLB QBench is a test retrieval service that uses Qdrant vector database with cloud embeddings to provide semantic search over test cases. The system ingests test data from multiple JSON sources, normalizes fields across different formats, and exposes a FastAPI interface for AI-powered test discovery.

## Key Development Commands

```bash
# Setup and Installation
pip install -e .                     # Install project in editable mode
pip install -e ".[dev]"             # Install with dev dependencies

# Docker/Services
make qdrant-up                      # Start Qdrant vector database (port 6533)
make qdrant-down                    # Stop Qdrant
make dev                            # Start both Qdrant and API server
make stop                           # Stop all services
make clean                          # Stop services and clean all data

# Development Server
make api-dev                        # Start FastAPI server (port 8000)
cd src/service && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Data Operations
python -m src.models.schema         # Create/recreate Qdrant collections
make ingest                         # Ingest all test data
python -m src.ingest.ingest_functional data/functional_tests_normalized.json
python -m src.ingest.ingest_api data/api_tests_normalized.json

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

### Dual Collection Design
The system uses two Qdrant collections for different search granularities:

1. **test_docs**: Document-level embeddings
   - One vector per test case containing title + description
   - Stores all test metadata (jiraKey, priority, tags, platforms, etc.)
   - Optimized for finding tests by their overall purpose

2. **test_steps**: Step-level embeddings  
   - One vector per test step containing action + expected result
   - Links to parent document via `parent_uid`
   - Enables finding tests by specific actions or validations

### Provider-Agnostic Embedding System
The `embedder.py` module implements a factory pattern:
- Base `EmbeddingProvider` class defines the interface
- Concrete implementations for OpenAI, Cohere, Vertex AI, Azure
- Provider selected via `EMBED_PROVIDER` environment variable
- Automatic batching and retry logic built-in

### Data Normalization Pipeline
Two ingestion modules handle different test formats:
- `ingest_functional.py`: Processes Xray functional tests
- `ingest_api.py`: Processes API test format
- Both normalize to common schema defined in `test_models.py`
- Key mappings: `labels` → `tags`, `folder` → `folderStructure`

### Hybrid Search Algorithm
The search endpoint (`/search`) implements:
1. Embeds user query using configured provider
2. Searches both collections in parallel
3. Applies filters to both result sets
4. Merges results with configurable weights (0.7 doc, 0.3 step)
5. Reranks by combined scores
6. Returns top-k results with matched steps included

### API Endpoints
- `POST /search`: Main semantic search with filters
- `POST /ingest`: Trigger data ingestion
- `GET /by-jira/{key}`: Direct lookup by JIRA key
- `GET /similar/{uid}`: Find similar tests
- `GET /health`: Service and collection health

### MCP Server Integration
The project includes an MCP (Model Context Protocol) server for AI tool integration:
- Located in `src/mcp/server.py`
- Exposes search and ingestion capabilities as tools
- Configured via `mcp.json` for Claude Desktop integration
- Start with `make mcp-server` or `python -m src.mcp`

## Environment Configuration

Required environment variables:
```bash
# Qdrant Configuration
QDRANT_URL=http://localhost:6533    # Custom port to avoid conflicts
# NOTE: Not using Qdrant Cloud - no API key needed for local Docker instance

# Embedding Provider
EMBED_PROVIDER=openai               # Options: openai, cohere, vertex, azure
EMBED_MODEL=text-embedding-3-large  # Model varies by provider

# Provider API Keys (set the one you're using)
OPENAI_API_KEY=your-key
COHERE_API_KEY=your-key
VERTEX_PROJECT=your-project
AZURE_OPENAI_ENDPOINT=your-endpoint

# API Authentication (optional)
MASTER_API_KEY=your-master-key      # Admin access for all operations
API_KEYS=key1,key2,key3            # Comma-separated list of valid API keys
```

## Key Technical Decisions

### Idempotent Ingestion
- Always check if UID exists before inserting
- Delete existing document and its steps before re-ingestion
- Ensures consistency when re-running ingestion

### HNSW Index Configuration
- `m=32, ef_construct=128` for initial 10k documents
- Can scale to 100k+ without reconfiguration
- Indexes on all filterable fields for performance

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

- Full ingestion of 1000 tests takes ~2-3 minutes with embeddings
- Search latency typically <100ms for hybrid search
- Memory usage scales with batch size settings
- Qdrant uses ~500MB RAM for 10k documents

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

### Qdrant Connection Failed
1. Check if Qdrant is running: `docker ps | grep qdrant`
2. Verify port 6533 is not in use: `lsof -i :6533`
3. Check Qdrant logs: `docker logs mlb-qbench-qdrant`