# MLB QBench - Test Retrieval Service

A local-only test retrieval service using Qdrant vector database with cloud embeddings. Ingests test data from multiple JSON sources, harmonizes fields, and provides a FastAPI interface for semantic search.

## Features

- **Dual Collection Architecture**: Separate collections for document-level and step-level search
- **Multi-Provider Embeddings**: Support for OpenAI, Cohere, Vertex AI, and Azure
- **Field Harmonization**: Unified schema across functional and API test sources
- **Hybrid Search**: Combined document and step-level semantic search with filtering
- **Idempotent Ingestion**: Safe re-ingestion with automatic updates

## Quick Start

### 1. Prerequisites

- Docker and Docker Compose
- Python 3.9+
- API key for your chosen embedding provider

### 2. Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/mlb-qbench.git
cd mlb-qbench

# Copy environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Install Python dependencies
pip install -e .
```

### 3. Start Services

```bash
# Start Qdrant and API server
make dev

# Or start services separately
make qdrant-up    # Start only Qdrant
make api-dev      # Start only API (requires Qdrant running)
```

### 4. Create Collections

```bash
# Initialize Qdrant collections
python -m src.models.schema
```

### 5. Ingest Test Data

```bash
# Ingest functional tests
python -m src.ingest.ingest_functional data/functional_tests_xray.json

# Ingest API tests
python -m src.ingest.ingest_api data/api_tests_xray.json

# Or use the Makefile
make ingest
```

## Configuration

### Environment Variables

```ini
# Qdrant Configuration
QDRANT_URL=http://localhost:6533
QDRANT_API_KEY=  # Optional

# Embedding Provider (openai, cohere, vertex, azure)
EMBED_PROVIDER=openai
EMBED_MODEL=text-embedding-3-large

# Provider-specific keys
OPENAI_API_KEY=your-key-here
```

See `.env.example` for all available options.

## API Endpoints

### Search

```bash
# Semantic search across tests
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Spanish localization on Team Page",
    "top_k": 20,
    "filters": {
      "tags": ["localization"]
    }
  }'
```

### Ingest

```bash
# Trigger ingestion via API
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "functional_path": "data/functional_tests_xray.json",
    "api_path": "data/api_tests_xray.json"
  }'
```

### Lookup

```bash
# Get test by JIRA key
curl http://localhost:8000/by-jira/FRAMED-1390

# Find similar tests
curl http://localhost:8000/similar/FRAMED-1390?scope=docs
```

## Data Schema

### Normalized Test Document

```json
{
  "uid": "FRAMED-1390",
  "jiraKey": "FRAMED-1390",
  "title": "English Language - Team Page API",
  "priority": "High",
  "tags": ["team_page", "api", "localization"],
  "steps": [
    {
      "index": 1,
      "action": "Send GET request",
      "expected": ["200 status"]
    }
  ]
}
```

See `docs/normalized_test.schema.json` for complete schema.

## Architecture

### Collections

1. **test_docs**: Document-level vectors for test metadata
   - HNSW index optimized for ~10k documents
   - Payload indexes on all filter fields

2. **test_steps**: Step-level vectors for granular search
   - Links to parent document via `parent_uid`
   - Enables finding tests by specific step content

### Search Algorithm

1. Query both collections with user's search text
2. Apply filters to both result sets
3. Merge results prioritizing document matches
4. Rerank by combined scores
5. Return top-k results with matched steps

### MCP Integration

MLB QBench includes an MCP (Model Context Protocol) server that allows AI assistants to interact with the service:

```bash
# Run the MCP server
python -m src.mcp

# Or configure in Claude Desktop
# See docs/MCP_USAGE.md for details
```

## Development

### Running Tests

```bash
make test
```

### Code Quality

```bash
make lint    # Run linters
make format  # Format code
```

### Project Structure

```
mlb-qbench/
├── src/
│   ├── models/          # Pydantic models and Qdrant schema
│   ├── ingest/          # Data ingestion and normalization
│   ├── service/         # FastAPI application
│   └── embedder.py      # Embedding provider wrapper
├── tests/               # Test suite
├── docs/                # Documentation
└── data/                # Sample test data
```

## Example Queries

### Localization Tests
```
"Spanish localization on Team Page"
→ Returns both API and functional tests with localization tags
```

### Live Game Tests
```
"Live game MIG validations"
→ Matches tests with live_state and requires_live_game tags
```

### Event-Specific Tests
```
"Jewel event regressions"
→ Finds both document and step-level matches for jewel_event
```

## Troubleshooting

### Qdrant Connection Issues

```bash
# Check if Qdrant is running
docker-compose ps

# View Qdrant logs
docker-compose logs qdrant

# Test connection
curl http://localhost:6533/health
```

### Embedding Errors

- Verify API keys in `.env`
- Check rate limits for your provider
- Enable debug logging: `LOG_LEVEL=DEBUG`

### Ingestion Issues

- Ensure JSON files match expected format
- Check for duplicate UIDs in logs
- Verify collections exist: `make check-env`

## Performance Tuning

### HNSW Parameters

- `m=32`: Good for datasets up to 100k
- `ef_construction=128`: Balance between index quality and build time
- Adjust based on recall requirements

### Batch Sizes

- Embedding: 100 texts per batch (configurable)
- Ingestion: 50 documents per batch
- Adjust based on memory constraints

## Documentation

- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) - Detailed design and architecture
- [Implementation Status](docs/IMPLEMENTATION_STATUS.md) - Current progress and remaining tasks
- [Normalized Schema](docs/normalized_test.schema.json) - Canonical test document format
- [MCP Usage](docs/MCP_USAGE.md) - Model Context Protocol integration guide

## License

MIT License - see LICENSE file
