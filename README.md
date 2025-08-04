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
2. **test_steps**: Step-level embeddings for finding tests by specific actions or validations

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
