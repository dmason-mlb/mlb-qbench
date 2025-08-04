# MLB QBench - Source Code Documentation

> Developer documentation for the MLB QBench source code architecture and modules

## Navigation

← **[Project Root](../README.md)** | **[API Documentation](../docs/API_DOCUMENTATION.md)** | **[Implementation Status](../docs/IMPLEMENTATION_STATUS.md)**

## Overview

This directory contains the core source code for MLB QBench, a high-performance test retrieval service built with FastAPI and Qdrant vector database. The codebase follows a modular architecture with clear separation of concerns and async-first design patterns.

## Directory Structure

```
src/
├── __init__.py                    # Package initialization
├── container.py                   # Dependency injection container
├── embedder.py                    # Provider-agnostic embedding factory
├── auth/                          # Authentication and authorization
│   ├── __init__.py               # Auth module exports
│   ├── auth.py                   # FastAPI auth dependencies
│   ├── models.py                 # Auth data models
│   └── secure_key_manager.py     # API key management system
├── ingest/                        # Data ingestion pipeline
│   ├── __init__.py               # Ingest module exports
│   ├── ingest_api.py             # API test format ingestion
│   ├── ingest_functional.py      # Xray functional test ingestion
│   └── normalize.py              # Data normalization utilities
├── mcp/                           # Model Context Protocol server
│   ├── __init__.py               # MCP module exports
│   ├── __main__.py               # MCP server entry point
│   └── server.py                 # MCP server implementation
├── models/                        # Data models and database schema
│   ├── __init__.py               # Models module exports
│   ├── filter_models.py          # Search filter models
│   ├── schema.py                 # Qdrant collection schemas
│   └── test_models.py            # Test document models
├── security/                      # Security utilities and validation
│   ├── __init__.py               # Security module exports
│   ├── jira_validator.py         # JIRA key validation
│   └── path_validator.py         # Path traversal protection
└── service/                       # FastAPI application
    ├── __init__.py               # Service module exports
    └── main.py                   # FastAPI app and endpoints
```

## Core Architecture Components

### Dependency Injection Container (`container.py`)

The application uses a custom dependency injection container that manages service lifecycles and dependencies:

- **ServiceDescriptor**: Defines service creation and management
- **Container**: Main DI container with singleton and transient scopes
- **configure_services()**: Bootstrap function that configures all services

```python
# Service registration example
container.register(EmbeddingProvider, OpenAIEmbedder, dependencies=['openai_client'])
container.register('qdrant_client', lambda: QdrantClient(url=os.getenv('QDRANT_URL')))
```

### Embedding System (`embedder.py`)

Provider-agnostic embedding system with async support:

- **EmbeddingProvider**: Abstract base class for embedding providers
- **OpenAIEmbedder, CohereEmbedder, VertexAIEmbedder, AzureEmbedder**: Provider implementations
- **get_embedder()**: Factory function that returns configured provider
- **Batch Processing**: Intelligent batching with configurable sizes (default: 25 texts/batch)
- **Retry Logic**: Automatic retry with exponential backoff using AsyncRetrying

```python
# Usage example
embedder = await container.get_async('embedder')
embeddings = await embedder.embed(["text1", "text2", "text3"])
```

### Authentication Module (`auth/`)

Enterprise-grade authentication system:

- **auth.py**: FastAPI dependencies for API key validation
- **models.py**: Pydantic models for auth data structures
- **secure_key_manager.py**: Secure API key storage and validation

Key features:
- Master key for admin operations
- Multiple user API keys support
- Secure key hashing and validation
- Rate limiting integration

### Data Ingestion Pipeline (`ingest/`)

Async data ingestion system for different test formats:

- **ingest_api.py**: Processes API test format with concurrent embedding generation
- **ingest_functional.py**: Handles Xray functional tests with async batch operations
- **normalize.py**: Data normalization utilities for consistent schema mapping

Both modules implement:
- Idempotent ingestion (checks for existing UIDs)
- Batch processing for performance
- Comprehensive error handling

### Model Context Protocol Server (`mcp/`)

AI assistant integration via MCP:

- **server.py**: MCP server implementation exposing search and ingestion tools
- **__main__.py**: Entry point for running MCP server standalone
- Configured via `mcp.json` for Claude Desktop integration

### Data Models (`models/`)

Pydantic models and database schemas:

- **test_models.py**: Core test document and step models
- **filter_models.py**: Search filter and query models
- **schema.py**: Qdrant collection configuration and health checks

### Security Utilities (`security/`)

Security validation and protection:

- **jira_validator.py**: JIRA key format validation with comprehensive patterns
- **path_validator.py**: Path traversal attack prevention
- Input sanitization and validation

### FastAPI Service (`service/`)

Main application entry point:

- **main.py**: FastAPI app with all endpoints, middleware, and lifecycle management
- Async endpoints with concurrent processing
- Rate limiting, CORS, and security middleware
- Comprehensive error handling and logging

## Key Design Patterns

### Async-First Architecture

All I/O operations use async/await patterns:
- Embedding API calls
- Database operations
- File I/O operations
- HTTP request handling

### Factory Pattern

Used extensively for provider abstraction:
- Embedding providers (`get_embedder()`)
- Service configuration (`configure_services()`)

### Dependency Injection

Central container manages all service dependencies:
- Singleton pattern for shared resources
- Transient pattern for request-scoped objects
- Automatic dependency resolution

### Dual Collection Design

Separate Qdrant collections for different search granularities:
- **test_docs**: Document-level embeddings with metadata
- **test_steps**: Step-level embeddings for action-specific search

## Development Workflow

### Adding New Modules

1. Create new directory under `src/`
2. Add `__init__.py` with module exports
3. Register services in `container.py` if needed
4. Add imports to relevant modules
5. Update this documentation

### Adding New Embedding Providers

1. Inherit from `EmbeddingProvider` in `embedder.py`
2. Implement `_embed_batch()` method
3. Add to `get_embedder()` factory function
4. Add environment variables and configuration

### Extending API Endpoints

1. Add new endpoints to `service/main.py`
2. Create Pydantic models in `models/`
3. Add authentication decorators if needed
4. Update API documentation

## Testing

Tests are located in the `../tests/` directory and cover:
- Unit tests for individual modules
- Integration tests for API endpoints
- Security tests for validation logic
- Performance tests for async operations

Run tests from project root:
```bash
make test                    # Full test suite with coverage
pytest tests/ -v            # Verbose test output
```

## Performance Considerations

- **Embedding Batching**: 25 texts per batch (configurable)
- **Async Operations**: Concurrent embedding and search operations
- **Memory Management**: Proper async resource cleanup
- **Connection Pooling**: Shared clients for external services

## Security Features

- **API Key Authentication**: Secure key validation and management
- **Rate Limiting**: Per-endpoint rate limits to prevent abuse
- **Input Validation**: Comprehensive input sanitization
- **Path Protection**: Prevention of path traversal attacks
- **CORS Configuration**: Configurable allowed origins

## Error Handling

Comprehensive error handling with:
- Structured logging with structlog
- Async-compatible retry logic
- Graceful degradation for external service failures
- Detailed error responses with appropriate HTTP status codes

---

**Updated on August 4, 2025**