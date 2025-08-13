# MLB QBench - Test Retrieval Service

> A high-performance test retrieval service using Qdrant vector database with cloud embeddings for semantic search over test cases

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

MLB QBench is a local-only test retrieval service that provides semantic search capabilities over test cases using vector embeddings. The system ingests test data from multiple JSON sources, normalizes fields across different formats, and exposes a FastAPI interface for AI-powered test discovery.

### Key Features

- **🚀 Async Architecture**: Fully async FastAPI service with concurrent processing and batch operations
- **🔍 Dual Collection Search**: Separate collections for document-level and step-level semantic search
- **🤖 Multi-Provider Embeddings**: Support for OpenAI, Cohere, Vertex AI, and Azure with intelligent batching
- **⚡ High Performance**: ~50% faster search through concurrent operations, 25x faster ingestion
- **🔐 Enterprise Security**: API key authentication, rate limiting, CORS protection, path validation
- **🧠 AI Integration**: Model Context Protocol (MCP) server for seamless AI assistant integration
- **📊 Comprehensive Monitoring**: Resource usage tracking and performance metrics

## Architecture

### Dual Collection Design

The system uses two Qdrant collections for different search granularities:

1. **test_docs**: Document-level embeddings containing title + description with full test metadata
   - Uses auto-incrementing `testId` as primary identifier
   - JIRA keys are optional and can be updated after test creation
2. **test_steps**: Step-level embeddings for finding tests by specific actions or validations
   - References parent tests via `parent_test_id`

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
│   ├── models/              # Pydantic models and Qdrant schema
│   ├── security/            # Security utilities and validation
│   ├── service/             # FastAPI application and endpoints
│   ├── container.py         # Dependency injection container
│   └── embedder.py          # Async embedding provider factory
├── tests/                   # Comprehensive test suite (11 test files)
├── docs/                    # Documentation and schema files
├── scripts/                 # Utility and development scripts
├── docker-compose.yml       # Qdrant database service
├── Makefile                 # Development workflow automation
└── pyproject.toml          # Project configuration and dependencies
```

## Quick Start

### Prerequisites

- **Docker & Docker Compose**: For Qdrant vector database
- **Python 3.9+**: Core runtime requirement
- **API Key**: For your chosen embedding provider (OpenAI, Cohere, Vertex AI, or Azure)

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
# Start all services (Qdrant + API)
make dev

# Or start components separately:
make qdrant-up                     # Start Qdrant database only
make api-dev                       # Start API server only (port 8000)
```

### Data Operations

```bash
# Create/recreate Qdrant collections
python -m src.models.schema

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
# Qdrant Database
QDRANT_URL=http://localhost:6533          # Custom port to avoid conflicts
QDRANT_API_KEY=                           # Optional for local Docker instance

# Embedding Provider (choose one)
EMBED_PROVIDER=openai                     # Options: openai, cohere, vertex, azure
EMBED_MODEL=text-embedding-3-large       # Model varies by provider
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

## Qdrant Database Setup

MLB QBench uses Qdrant as its vector database for semantic search capabilities. The system automatically configures two collections optimized for different search patterns.

### Starting Qdrant

```bash
# Start Qdrant using Docker Compose
make qdrant-up

# Or manually with docker-compose
docker-compose up -d qdrant

# Verify Qdrant is running
docker ps | grep qdrant
curl http://localhost:6533/health
```

### Qdrant Configuration

The system uses these port mappings to avoid conflicts:
- **REST API**: `localhost:6533` (internal: 6333)
- **gRPC**: `localhost:6534` (internal: 6334)
- **Storage**: `./qdrant_storage/` (persistent volume)

### Collection Architecture

The system automatically creates two optimized collections:

#### 1. `test_docs` - Document-Level Search
- **Purpose**: Find tests by overall content (title + description)
- **Vector Size**: 3072 dimensions (OpenAI text-embedding-3-large)
- **HNSW Config**: `m=32, ef_construct=128` for 10k+ documents
- **Indexed Fields**: `priority`, `testType`, `platforms`, `tags`, `folderStructure`

#### 2. `test_steps` - Step-Level Search  
- **Purpose**: Find tests by specific actions or validation steps
- **Vector Size**: 3072 dimensions
- **Parent Linking**: Each step links to parent document via `parent_uid`
- **Indexed Fields**: `parent_uid`, `step_index`

### Collection Management

```bash
# Create/recreate collections (WARNING: deletes existing data)
python -m src.models.schema

# Check collection health and stats
curl -H "X-API-Key: your-key" http://localhost:8000/healthz

# View collections in Qdrant dashboard (if enabled)
open http://localhost:6533/dashboard
```

### Troubleshooting Qdrant

**Connection Issues**:
```bash
# Check if Qdrant is running
docker logs mlb-qbench-qdrant

# Restart with clean state
make clean
make qdrant-up
```

**Storage Permission Issues**:
```bash
# Fix permissions (macOS/Linux)
rm -rf qdrant_storage
mkdir qdrant_storage
chmod 755 qdrant_storage
```

**Port Conflicts**:
```bash
# Check what's using the ports
lsof -i :6533
lsof -i :6534

# Kill conflicting processes or change ports in docker-compose.yml
```

## Test Data Ingestion

The system supports ingesting test data from standardized JSON formats. All test data is normalized to a common schema regardless of source format.

### Supported Input Formats

#### 1. Functional Tests (Xray Format)
```json
{
  "issueKey": "FRAMED-1390",
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
  "jiraKey": "API-5678",
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
- **`uid`**: Unique identifier (derived from `jiraKey` or `testCaseId`)
- **`title`**: Test name/summary 
- **`source`**: Source filename (auto-generated during ingestion)
- **`ingested_at`**: Timestamp (auto-generated during ingestion)

### Field Normalization

The ingestion process automatically normalizes fields:

| Source Field | Target Field | Notes |
|--------------|--------------|-------|
| `labels` | `tags` | Unified tagging system |
| `folder` | `folderStructure` | Path standardization |
| `issueKey` | `jiraKey` | JIRA key consistency |
| `testSteps` | `steps` | Step format unification |
| `expectedResult` | `expected` | Array format |
| `result` | `expected` | Functional → API format |

### Ingestion Commands

```bash
# Ingest functional tests
python -m src.ingest.ingest_functional /path/to/functional_tests.json

# Ingest API tests  
python -m src.ingest.ingest_api /path/to/api_tests.json

# Batch ingestion (if files exist in data/ directory)
make ingest

# Ingestion with custom embedder settings
EMBED_PROVIDER=openai python -m src.ingest.ingest_functional tests.json
```

### Ingestion Process

The ingestion pipeline follows these steps:

1. **Validation**: JSON schema validation and security checks
2. **Normalization**: Field mapping and data standardization  
3. **Embedding**: Generate vectors for titles, descriptions, and steps
4. **Batch Processing**: Process in batches of 25 documents for efficiency
5. **Upsert**: Insert/update in Qdrant with idempotent operations
6. **Verification**: Confirm successful ingestion and indexing

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

- **Ingestion Speed**: ~25x faster with async batch processing
- **Batch Size**: 25 documents per batch (configurable)
- **Embedding Batching**: 25 texts per API call (configurable)  
- **Rate Limiting**: 5 requests/minute for ingestion endpoint
- **Memory Usage**: ~100MB per 1000 documents during ingestion

### Validation and Troubleshooting

```bash
# Validate JSON format before ingestion
python -c "
import json
with open('your_tests.json') as f:
    data = json.load(f)
    print(f'Loaded {len(data)} test records')
    print('Required fields present:', all('title' in test for test in data))
"

# Check ingestion logs
tail -f logs/ingestion.log

# Verify collection counts after ingestion
curl http://localhost:6533/collections/test_docs | jq '.result.points_count'
curl http://localhost:6533/collections/test_steps | jq '.result.points_count'
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

# Direct JIRA key lookup
curl http://localhost:8000/by-jira/{jira_key}
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
make qdrant-down                       # Stop Qdrant only
```

## AI Integration (MCP)

The project includes a Model Context Protocol server for AI assistant integration:

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

- **Search Latency**: Typically <100ms for hybrid search queries
- **Ingestion Speed**: 25x improvement through async batch processing
- **Memory Usage**: ~500MB RAM for 10k documents in Qdrant
- **Concurrent Operations**: ~50% faster search through async processing
- **Rate limits**: 60 requests/minute for search, 5/minute for ingestion

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
rm -rf qdrant_storage && mkdir qdrant_storage
make qdrant-up
```

**Module Import Errors**:
```bash
pip install -e .                      # Ensure editable installation
```

**Qdrant Connection Failed**:
```bash
docker ps | grep qdrant                # Check if running
lsof -i :6533                         # Check port availability
docker logs mlb-qbench-qdrant         # Check Qdrant logs
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

- Built with FastAPI and Qdrant for high-performance vector search
- Supports multiple embedding providers for flexibility
- Designed for MLB's test discovery and automation needs
