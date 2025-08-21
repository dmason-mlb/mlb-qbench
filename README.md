# MLB QBench - Test Retrieval Service

> A high-performance test retrieval service using PostgreSQL with pgvector extension and cloud embeddings for semantic search over test cases

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MLB QBench is a test retrieval service that provides semantic search capabilities over test cases using PostgreSQL with pgvector extension. The system ingests test data from multiple sources including TestRail SQLite databases (104k+ tests), normalizes fields across different formats, and exposes a FastAPI interface for AI-powered test discovery.

### Key Features

- **🚀 PostgreSQL + pgvector**: Scalable vector database with HNSW indexes for 100-1000x faster similarity search
- **🔍 Dual Table Design**: Separate tables for document-level and step-level semantic search
- **🤖 Optimized Embeddings**: OpenAI text-embedding-3-small (1536 dimensions) for 5x cost reduction
- **⚡ High Performance**: 50+ docs/second migration, <100ms search latency with vector indexes
- **📦 TestRail Integration**: Direct migration from TestRail SQLite databases (104k+ tests)
- **🔐 Enterprise Security**: API key authentication, rate limiting, CORS protection, path validation
- **🧠 AI Integration**: Model Context Protocol (MCP) server for seamless AI assistant integration
- **📊 Comprehensive Monitoring**: Resource usage tracking and performance metrics

## Architecture

### Dual Table Design

The system uses two PostgreSQL tables with vector columns for different search granularities:

1. **test_documents**: Document-level embeddings containing title + description with full test metadata
   - Uses `test_case_id` from TestRail as primary identifier
   - Test identifiers preserved from TestRail data
   - HNSW index on 1536-dimension vectors for fast similarity search
2. **test_steps**: Step-level embeddings for finding tests by specific actions or validations
   - References parent tests via foreign key to test_documents
   - Separate HNSW index for step-level search

### Async Provider-Agnostic Embedding System

- Factory pattern with async `EmbeddingProvider` base class
- Concurrent batch processing (25 texts/batch by default)
- Automatic retry logic with exponential backoff
- Proper async resource management and cleanup

## Directory Structure

```
mlb-qbench/
├── src/
│   ├── auth/                 # API key authentication system
│   ├── ingest/              # Async data ingestion modules
│   │   ├── ingest_api.py    # API test format ingestion
│   │   └── ingest_functional.py  # Xray functional test ingestion
│   ├── mcp/                 # Model Context Protocol server
│   ├── models/              # Pydantic models and data schemas
│   ├── security/            # Security utilities and validation
│   ├── service/             # FastAPI application and endpoints
│   ├── container.py         # Dependency injection container
│   └── embedder.py          # Async embedding provider factory
├── tests/                   # Comprehensive test suite (11 test files)
├── docs/                    # Documentation and schema files
├── scripts/                 # Utility and development scripts
├── docker-compose.yml       # PostgreSQL database service
├── Makefile                 # Development workflow automation
└── pyproject.toml          # Project configuration and dependencies
```

## Quick Start

### Prerequisites

- **PostgreSQL 15+**: With pgvector extension for vector similarity search
- **Python 3.10+**: Core runtime requirement
- **OpenAI API Key**: For text-embedding-3-small embeddings

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd mlb-qbench

# Install dependencies
pip install -e .                    # Core dependencies
pip install -e ".[dev]"            # Include development tools

# Copy and configure environment
cp .env.example .env
# Edit .env with your API keys and configuration

# Create data directory for test JSON files (optional)
mkdir -p data
# Place your test JSON files in data/ directory for batch ingestion
```

### Development Setup

```bash
# Start API server with PostgreSQL
make dev

# Or run directly:
make api-dev                       # Start API server only (port 8000)
```

### Data Operations

```bash
# Create PostgreSQL schema
make postgres-schema

# Ingest test data (requires JSON files in data/ directory)
make ingest

# Manual ingestion
python -m src.ingest.ingest_functional data/functional_tests_normalized.json
python -m src.ingest.ingest_api data/api_tests_normalized.json
```

## Environment Configuration

Configure your environment by copying `.env.example` to `.env` and setting the required variables:

### Core Configuration

```bash
# PostgreSQL Database
DATABASE_URL=postgresql://username@localhost/mlb_qbench

# Embedding Provider
EMBED_PROVIDER=openai                     # Currently optimized for OpenAI
EMBED_MODEL=text-embedding-3-small       # 1536 dimensions for pgvector compatibility
```

### Security Configuration

```bash
# API Authentication (optional but recommended)
MASTER_API_KEY=your-secure-master-key     # Admin access for all operations
API_KEYS=key1,key2,key3                   # Comma-separated user API keys
CORS_ORIGINS=http://localhost:3000        # Allowed CORS origins
```

### Provider API Keys

Set the appropriate API key for your chosen embedding provider:

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

## PostgreSQL Database Setup

MLB QBench uses PostgreSQL with pgvector extension for semantic search capabilities. The system creates optimized tables with HNSW indexes for fast vector similarity search.

### Database Setup

```bash
# Install pgvector extension (macOS with Homebrew)
brew install pgvector

# Create database and enable extension
createdb mlb_qbench
psql -d mlb_qbench -c "CREATE EXTENSION vector;"

# Create schema with optimized 1536-dimension vectors
psql -d mlb_qbench < sql/create_schema_1536.sql
```

### PostgreSQL Configuration

The system uses PostgreSQL with pgvector extension:
- **Database**: `mlb_qbench` on `localhost:5432`
- **Extension**: pgvector for similarity search
- **Storage**: `./postgres_data/` (persistent volume)

### Collection Architecture

The system automatically creates two optimized collections:

#### 1. `test_documents` - Document-Level Search
- **Purpose**: Find tests by overall content (title + description)
- **Vector Size**: 1536 dimensions (OpenAI text-embedding-3-small)
- **HNSW Config**: `m=16, ef_construction=64` optimized for 100k+ documents
- **Indexed Fields**: `test_case_id`, `priority`, `test_type`, `platforms`, `tags`, `folder_structure`
- **TestRail Fields**: Preserves `suite_id`, `section_id`, `project_id`, `custom_fields`

#### 2. `test_steps` - Step-Level Search  
- **Purpose**: Find tests by specific actions or validation steps
- **Vector Size**: 1536 dimensions
- **Parent Linking**: Foreign key to test_documents with CASCADE delete
- **Indexed Fields**: `test_document_id`, `step_index`

### Migration from TestRail

```bash
# Run optimized migration for 104k+ tests
make migrate-optimized

# Or with custom settings
python scripts/migrate_optimized.py --batch-size 500 --checkpoint-interval 5000

# Resume interrupted migration
make migrate-resume-optimized

# Check migration progress
tail -f migration.log | grep "Migration progress"
```

### Troubleshooting PostgreSQL

**Connection Issues**:
```bash
# Check if PostgreSQL is running
pg_isready
psql -l | grep mlb_qbench

# Check pgvector installation
psql -d mlb_qbench -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
```

**Schema Issues**:
```bash
# Verify schema exists
psql -d mlb_qbench -c "\dt"  # Should show test_documents, test_steps tables

# Recreate schema if needed
make postgres-schema
```

**Permission Issues**:
```bash
# Fix permissions (macOS/Linux)
rm -rf postgres_data
mkdir postgres_data
chmod 755 postgres_data
```

## Test Data Ingestion

The system supports ingesting test data from standardized JSON formats. All test data is normalized to a common schema regardless of source format.

### Supported Input Formats

#### 1. Functional Tests (Xray Format)
```json
{
  "testCaseId": "tc_func_001",
  "testInfo": {
    "summary": "Login functionality test",
    "description": "Verify user can log in with valid credentials",
    "type": "Manual", 
    "priority": "High",
    "labels": ["login", "authentication", "web"]
  },
  "folder": "/Web/Authentication",
  "preconditions": ["User account exists", "Application is accessible"],
  "steps": [
    {
      "index": 1,
      "action": "Navigate to login page",
      "data": "https://app.example.com/login",
      "result": "Login page displays correctly"
    },
    {
      "index": 2, 
      "action": "Enter valid username and password",
      "data": "username=testuser, password=securepass",
      "result": "Credentials accepted, user logged in"
    }
  ]
}
```

#### 2. API Tests (Normalized Format)
```json
{
  "testCaseId": "tc_api_001", 
  "title": "User Authentication API",
  "testType": "API",
  "priority": "High",
  "platforms": ["iOS", "Android", "Web"],
  "folderStructure": "API Tests/Authentication", 
  "tags": ["api", "auth", "login"],
  "preconditions": ["API endpoint available", "Valid test credentials"],
  "testSteps": [
    {
      "action": "POST /api/auth/login with valid credentials",
      "expectedResult": "200 OK with JWT token"
    },
    {
      "action": "Verify token structure and expiration", 
      "expectedResult": "Valid JWT with 1 hour expiration"
    }
  ],
  "testData": "username=testuser, endpoint=/api/auth/login",
  "relatedIssues": ["FRAMED-1234", "FRAMED-5678"],
  "testPath": "tests/api/auth/test_login.py:45"
}
```

### Required Fields

All test records must include these minimum fields:
- **`uid`**: Unique identifier (derived from `testCaseId`)
- **`title`**: Test name/summary 
- **`source`**: Source filename (auto-generated during ingestion)
- **`ingested_at`**: Timestamp (auto-generated during ingestion)

### Field Normalization

The ingestion process automatically normalizes fields:

| Source Field | Target Field | Notes |
|--------------|--------------|-------|
| `labels` | `tags` | Unified tagging system |
| `folder` | `folderStructure` | Path standardization |
| `testSteps` | `steps` | Step format unification |
| `expectedResult` | `expected` | Array format |
| `result` | `expected` | Functional → API format |

### Ingestion Commands

```bash
# Standard ingestion (concurrent - for small/medium datasets)
python -m src.ingest.ingest_functional /path/to/functional_tests.json
python -m src.ingest.ingest_api /path/to/api_tests.json
make ingest

# Large-scale sequential ingestion (for 5,000+ documents)
python ingest_sequential.py                    # Process all batches in data/ directory
python ingest_all_testrail_improved.py         # Alternative with retry logic

# Custom embedder settings
EMBED_PROVIDER=openai python -m src.ingest.ingest_functional tests.json
```

### Large-Scale Ingestion Monitoring

For large datasets requiring sequential processing:

```bash
# Start sequential ingestion in background
nohup python ingest_sequential.py > ingestion.log 2>&1 &

# Monitor progress (use the provided monitoring script)
./monitor_ingestion.py

# Check process status
ps aux | grep "python ingest_sequential.py" | grep -v grep

# View recent log entries
tail -20 ingestion.log

# Check collection health during ingestion
python -c "
from src.models.schema import check_collections_health
health = check_collections_health()
for name, info in health['collections'].items():
    print(f'{name}: {info[\"status\"]} ({info[\"points_count\"]} points)')
"
```

### Ingestion Strategies

The system supports two ingestion approaches depending on dataset size and stability requirements:

#### 1. Concurrent Ingestion (Default - Small to Medium Datasets)

Optimized for datasets under 1,000 documents with high performance:

1. **Validation**: JSON schema validation and security checks
2. **Normalization**: Field mapping and data standardization  
3. **Batch Embedding**: Generate vectors concurrently in batches of 25 texts
4. **Concurrent Processing**: Process multiple documents simultaneously
5. **Batch Upsert**: Insert/update in PostgreSQL with idempotent operations
6. **Verification**: Confirm successful ingestion and indexing

**Performance**: ~25x faster through async batch processing

#### 2. Sequential Ingestion (Large Datasets)

Conservative approach for large datasets (5,000+ documents) to prevent database overload:

1. **One-at-a-time Processing**: Sequential embedding generation to minimize load
2. **Resource Management**: Health checks and controlled delays between batches
3. **Corruption Prevention**: Avoids concurrent API calls that can overwhelm the database
4. **Progress Monitoring**: Built-in progress tracking and recovery mechanisms
5. **Stability Focus**: Prioritizes data integrity over speed

**When to Use Sequential**:
- Large datasets (>5,000 documents)
- Previous ingestion corruption issues
- Resource-constrained environments
- Mission-critical data requiring guaranteed integrity

**Performance**: Slower but reliable (~1 embedding/second, 15-20 hours for 6,350 documents)

### Ingestion API Endpoint

```bash
# Ingest via REST API (requires authentication)
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "functional_path": "/path/to/functional_tests.json",
    "api_path": "/path/to/api_tests.json"
  }'
```

### Performance Metrics

#### Concurrent Ingestion (Small/Medium Datasets)
- **Ingestion Speed**: ~25x faster with async batch processing
- **Batch Size**: 25 documents per batch (configurable)
- **Embedding Batching**: 25 texts per API call (configurable)  
- **Memory Usage**: ~100MB per 1000 documents during ingestion
- **Recommended For**: <1,000 documents

#### Sequential Ingestion (Large Datasets)
- **Ingestion Speed**: ~1 embedding per second (conservative)
- **Processing**: One document at a time to prevent overload
- **Batch Size**: 10 records per database insert (with delays)
- **Memory Usage**: ~50MB constant (minimal buffering)
- **Recommended For**: >5,000 documents or after corruption issues
- **Typical Duration**: 15-20 hours for 6,350 documents

#### General Limits
- **Rate Limiting**: 5 requests/minute for ingestion endpoint
- **Health Checks**: Every 5 batches during sequential processing
- **Recovery**: Automatic retry with exponential backoff

### Validation and Troubleshooting

#### Pre-Ingestion Validation
```bash
# Validate JSON format before ingestion
python -c "
import json
with open('your_tests.json') as f:
    data = json.load(f)
    print(f'Loaded {len(data)} test records')
    print('Required fields present:', all('title' in test for test in data))
"

# Check collection health before starting large ingestion
python -c "
from src.models.schema import check_collections_health
health = check_collections_health()
print(f'Status: {health[\"status\"]}')
for name, info in health['collections'].items():
    print(f'{name}: {info[\"status\"]}')
"
```

#### Database Recovery
```bash
# Signs of issues: connection errors, slow queries
# Recovery steps:
make postgres-clean                           # Drop and recreate database
make postgres-schema                          # Recreate schema

# Use sequential ingestion to prevent recurrence
python ingest_sequential.py
```

#### During Large Ingestion
```bash
# Monitor active ingestion
./monitor_ingestion.py                        # Custom progress monitor
tail -f ingestion.log | grep -E "(✅|❌|Processing batch)"

# Check for worker failures
grep "channel closed" ingestion.log
grep "Service internal error" ingestion.log

# Verify collections stay healthy
curl http://localhost:6533/collections/test_docs | jq '.result.status'
curl http://localhost:6533/collections/test_steps | jq '.result.status'
```

#### Post-Ingestion Verification
```bash
# Verify final collection counts
curl http://localhost:6533/collections/test_docs | jq '.result.points_count'
curl http://localhost:6533/collections/test_steps | jq '.result.points_count'

# Test search functionality
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "limit": 5}'
```

## API Usage

### Search Endpoint

```bash
# Semantic search with filters
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "query": "login authentication test",
    "limit": 10,
    "filters": {
      "priority": ["High", "Critical"],
      "tags": ["api", "authentication"]
    }
  }'
```

### Additional Endpoints

```bash
# Health check
curl http://localhost:8000/healthz

# Performance metrics
curl http://localhost:8000/metrics

# Find similar tests
curl http://localhost:8000/similar/{test_uid}

# Direct test lookup by ID
curl http://localhost:8000/by-test/{test_id}
```

## Development Workflow

### Code Quality

```bash
make lint                              # Run ruff and mypy checks
make format                            # Format code with black and ruff
make test                              # Run full test suite with coverage
```

### Testing

```bash
pytest tests/ -v                       # Run tests with verbose output
pytest tests/test_specific.py -k "test_name"  # Run specific test
make test                              # Run with coverage reports
```

### Environment Verification

```bash
make check-env                         # Verify environment variables
make help                              # Show all available commands
```

### Service Management

```bash
make stop                              # Stop all services
make clean                             # Stop services and clean all data
```

## AI Integration (MCP)

The project includes a Model Context Protocol server for AI assistant integration with 5 specialized tools for test discovery and management. See the full catalog and usage examples in [TOOLSET.md](docs/TOOLSET.md).

```bash
# Start MCP server for AI tools
make mcp-server

# Configure in Claude Desktop (mcp.json)
{
  "mcpServers": {
    "mlb-qbench": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "cwd": "/path/to/mlb-qbench",
      "env": {
        "API_BASE_URL": "http://localhost:8000"
      }
    }
  }
}
```

## Performance Characteristics

- **Search Latency**: <100ms with HNSW indexes (100-1000x faster than sequential scan)
- **Migration Speed**: 50+ docs/second with optimized batch processing
- **Embedding Costs**: ~$1.04 for 104k tests with text-embedding-3-small (vs $6.76 with large)
- **Database Size**: ~2GB for 104k documents with vectors and indexes
- **Concurrent Operations**: Connection pooling with 20-50 async connections
- **Rate limits**: 60 requests/minute for search, 5/minute for ingestion
- **Scalability**: Successfully migrated 104,121 TestRail test cases

## Testing

The project includes comprehensive test coverage across 11 test files:

- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Security Tests**: Authentication and validation testing
- **Performance Tests**: Async operation and batch processing validation

```bash
make test                              # Full test suite with coverage
pytest tests/ -v --cov=src            # Verbose with coverage
```

## Troubleshooting

### Common Issues

**Docker Permission Errors**:
```bash
rm -rf postgres_data && mkdir postgres_data
docker-compose up -d postgres
```

**Module Import Errors**:
```bash
pip install -e .                      # Ensure editable installation
```

**PostgreSQL Connection Failed**:
```bash
docker ps | grep postgres              # Check if running
lsof -i :5432                         # Check port availability
docker logs mlb-qbench-postgres       # Check PostgreSQL logs
```

**Embedding API Issues**:
- Verify API key configuration: `make check-env`
- Check rate limits and quotas for your provider
- Review logs for specific error messages

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Follow the existing code style and run tests
4. Submit a pull request with clear description

### Development Guidelines

- Follow PEP 8 style guidelines (enforced by ruff and black)
- Add type hints for all functions (enforced by mypy)
- Write tests for new functionality
- Update documentation for API changes
- Use async/await patterns for I/O operations

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with FastAPI and PostgreSQL with pgvector for high-performance vector search
- Supports multiple embedding providers for flexibility
- Designed for MLB's test discovery and automation needs
