# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

MLB QBench is a high-performance test retrieval service using Qdrant vector database with cloud embeddings for semantic search over test cases. The system ingests test data from multiple JSON sources, normalizes fields across different formats, and exposes a FastAPI interface for AI-powered test discovery.

## Quick Start Commands

### Installation & Setup
```bash
# Install dependencies
pip install -e .                     # Core dependencies
pip install -e ".[dev]"             # Include development tools

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Database & Services
```bash
# Start Qdrant vector database only (port 6533)
make qdrant-up

# Start both Qdrant and API server
make dev

# Start only API server (assumes Qdrant running)
make api-dev

# Stop all services
make stop

# Stop services and clean all data
make clean
```

### Data Operations
```bash
# Create/recreate Qdrant collections
python -m src.models.schema

# Ingest test data
make ingest                          # Ingest all test data from data/
python -m src.ingest.ingest_functional data/functional_tests_normalized.json
python -m src.ingest.ingest_api data/api_tests_normalized.json
```

### Development
```bash
# Code quality
make lint                           # Run ruff and mypy
make format                         # Format with black and ruff

# Testing
make test                          # Run full test suite with coverage
pytest tests/ -v                   # Run tests verbose
pytest tests/test_specific.py -k "test_name"  # Run specific test

# Environment verification
make check-env                     # Verify environment variables
```

### AI Integration (MCP Server)
```bash
# Start MCP server for AI tools
make mcp-server
python -m src.mcp                  # Direct invocation
```

## Architecture Overview

### Dual Collection Design
The system uses two Qdrant collections for different search granularities:

1. **test_docs**: Document-level embeddings containing title + description with full test metadata
   - Uses auto-incrementing `testId` as primary identifier
   - JIRA keys are optional and can be updated after test creation

2. **test_steps**: Step-level embeddings for finding tests by specific actions or validations
   - References parent tests via `parent_test_id`
   - Enables granular search within test execution steps

### Async Provider-Agnostic Embedding System
- Factory pattern with async `EmbeddingProvider` base class (`src/embedder.py`)
- Concurrent batch processing (25 texts/batch by default)
- Supports OpenAI, Cohere, Vertex AI, and Azure embedding providers
- Automatic retry logic with exponential backoff
- 25x faster ingestion through async batch processing

### Key Components
- **FastAPI Service** (`src/service/main.py`): REST API with semantic search endpoints
- **Dependency Container** (`src/container.py`): Enterprise-grade DI container for service management
- **Ingestion Pipeline** (`src/ingest/`): Async data ingestion with normalization
- **Security Framework** (`src/auth/`, `src/security/`): API key auth, rate limiting, validation
- **MCP Server** (`src/mcp/`): Model Context Protocol for AI assistant integration

## Configuration Reference

### Core Environment Variables
```bash
# Qdrant Database
QDRANT_URL=http://localhost:6533          # Custom port to avoid conflicts
QDRANT_API_KEY=                           # Optional for local Docker instance

# Embedding Provider (choose one)
EMBED_PROVIDER=openai                     # Options: openai, cohere, vertex, azure
EMBED_MODEL=text-embedding-3-large       # Model varies by provider

# API Authentication (optional but recommended)
MASTER_API_KEY=your-secure-master-key     # Admin access for all operations
API_KEYS=key1,key2,key3                   # Comma-separated user API keys
CORS_ORIGINS=http://localhost:3000        # Allowed CORS origins
```

### Provider API Keys
Set the appropriate key for your chosen embedding provider:
```bash
# OpenAI
OPENAI_API_KEY=your-openai-key

# Cohere
COHERE_API_KEY=your-cohere-key

# Google Vertex AI
VERTEX_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

### Qdrant Configuration
- **REST API**: `localhost:6533` (internal: 6333)
- **gRPC**: `localhost:6534` (internal: 6334)
- **Storage**: `./qdrant_storage/` (persistent volume)

## Key Technical Insights

### Async Architecture & Performance
- **Concurrent Search**: Document and step searches execute in parallel using `asyncio.gather()`
- **Batch Embedding**: 25 texts per API call, dramatically reducing embedding generation time
- **Connection Pooling**: Efficient Qdrant client management through dependency injection
- **Rate Limiting**: 60 requests/minute for search, 5/minute for ingestion

### Data Normalization Strategy
- Field mappings: `labels` → `tags`, `folder` → `folderStructure`, `issueKey` → `jiraKey`
- Handles multiple input formats: Xray functional, Xray API, legacy JSON
- Idempotent ingestion: Always check if UID exists before inserting
- Sequential ingestion available for large datasets (5,000+ documents) to prevent Qdrant corruption

### Security & Validation
- API key authentication with master key for admin operations
- Input sanitization prevents injection attacks (SQL, XSS, path traversal)
- JIRA key validation with regex patterns
- Path validation for ingestion endpoints

### Service Container Pattern
The dependency injection container (`src/container.py`) manages:
- **Singleton Services**: Embedders, database clients (expensive to create)
- **Transient Services**: Validators, processors (lightweight, stateless)
- **Service Resolution**: Automatic dependency injection with circular detection
- **Async Cleanup**: Proper resource disposal during shutdown

### Collection Architecture
- **Vector Size**: 3072 dimensions (OpenAI text-embedding-3-large)
- **HNSW Config**: `m=32, ef_construct=128` optimized for 10k+ documents
- **Indexed Fields**: All filterable fields for performance
- **Memory Settings**: Collections kept in memory for maximum query speed

## MCP Tool Integration

The project includes 5 MCP tools for AI assistant integration:
- `search_tests`: Semantic search with natural language queries
- `get_test_by_jira`: Direct test lookup by JIRA key
- `find_similar_tests`: Similarity search based on reference test
- `ingest_tests`: Trigger test data ingestion
- `check_health`: Service health monitoring

## Directory Structure Notes

```
src/
├── auth/                 # API key authentication system
├── ingest/              # Async data ingestion modules
├── mcp/                 # Model Context Protocol server
├── models/              # Pydantic models and Qdrant schema
├── security/            # Security utilities and validation
├── service/             # FastAPI application and endpoints
├── container.py         # Dependency injection container
└── embedder.py          # Async embedding provider factory
```

## Common Troubleshooting

### Docker Permission Issues
```bash
rm -rf qdrant_storage && mkdir qdrant_storage
make qdrant-up
```

### Qdrant Connection Failed
```bash
docker ps | grep qdrant                # Check if running
lsof -i :6533                         # Check port availability
docker logs mlb-qbench-qdrant         # Check Qdrant logs
```

### Large Dataset Ingestion
For datasets over 5,000 documents, use sequential ingestion:
```bash
python ingest_sequential.py           # Conservative approach to prevent corruption
```

## Important Implementation Details

- The system supports both document-level and step-level semantic search
- Hybrid scoring combines document relevance (70%) with step matches (30%)
- All async operations use proper resource management with cleanup
- Service health checks validate both Qdrant connectivity and collection status
- The MCP server enables seamless AI assistant integration for test discovery

## Performance Characteristics

- **Search Latency**: Typically <100ms for hybrid search queries
- **Memory Usage**: ~500MB RAM for 10k documents in Qdrant
- **Ingestion Speed**: 25x improvement through async batch processing
- **Scalability**: Successfully tested with 6,350+ documents
- **Concurrent Operations**: ~50% faster search through async processing
