# MLB QBench Implementation Plan

## Project Overview

MLB QBench is a local-only test retrieval service using Qdrant vector database with cloud embeddings. It ingests test data from multiple JSON sources (functional/Xray + API tests), harmonizes fields, and exposes a FastAPI interface for AI-powered semantic search.

## Architecture

### Core Components

1. **Vector Database**: Qdrant running on custom ports (6533/6534)
2. **Embedding Service**: Provider-agnostic wrapper supporting OpenAI, Cohere, Vertex AI, Azure
3. **Data Ingestion**: Normalizes and ingests from two JSON formats
4. **Search API**: FastAPI service with hybrid search capabilities

### Collections Design

- **test_docs**: Document-level vectors for test metadata
  - One point per test case
  - Contains all test metadata and properties
  - Optimized for semantic search on test descriptions

- **test_steps**: Step-level vectors for granular search
  - One point per test step
  - Links to parent document via `parent_uid`
  - Enables finding tests by specific step content

## Implementation Phases

### Phase 1: Foundation ✅
- [x] Docker Compose configuration
- [x] Python project setup
- [x] Directory structure
- [x] Environment configuration
- [x] Development tooling (Makefile)

### Phase 2: Data Layer ✅
- [x] Pydantic models (TestDoc, TestStep)
- [x] Qdrant schema definition
- [x] Collection creation with indexes
- [x] Normalized JSON schema documentation

### Phase 3: Embedding Service ✅
- [x] Provider-agnostic base class
- [x] OpenAI implementation
- [x] Cohere implementation
- [x] Vertex AI implementation
- [x] Azure OpenAI implementation
- [x] Batching and error handling

### Phase 4: Data Normalization ✅
- [x] Field harmonization logic
- [x] Functional test normalization
- [x] API test normalization
- [x] UID handling with fallback
- [x] Validation and warnings

### Phase 5: Ingestion Pipeline ✅
- [x] Functional test ingestion
- [x] API test ingestion
- [x] Idempotent updates
- [x] Batch processing
- [x] Progress logging

### Phase 6: Search API ✅
- [x] FastAPI application
- [x] Search endpoint with hybrid algorithm
- [x] Ingest endpoint
- [x] By-JIRA lookup
- [x] Similar tests endpoint
- [x] Health check

### Phase 7: Testing & Documentation 🚧
- [ ] Unit tests for models
- [ ] Unit tests for normalization
- [ ] Integration tests for ingestion
- [ ] Integration tests for search
- [ ] Performance benchmarks
- [ ] API documentation

## Key Design Decisions

### 1. Dual Collection Architecture
- Separate collections for documents and steps
- Enables both high-level and granular search
- Maintains relationship via `parent_uid`

### 2. Field Harmonization
- Maps `labels` → `tags` from functional tests
- Maps `folder` → `folderStructure`
- Handles null `jiraKey` with `testCaseId` fallback

### 3. Hybrid Search Algorithm
1. Search both collections with user query
2. Apply filters to both result sets
3. Merge results with weighted scoring
4. Rerank by combined scores
5. Return top-k with matched steps

### 4. Provider-Agnostic Embeddings
- Factory pattern for provider selection
- Environment-based configuration
- Consistent interface across providers

### 5. Idempotent Operations
- Check existing UIDs before insert
- Delete old data before update
- Maintain consistency across collections

## Configuration

### HNSW Parameters
- `m=32`: Optimized for ~10k initial documents
- `ef_construction=128`: Balance quality vs build time
- Can scale to 100k+ documents

### Batch Sizes
- Embedding: 100 texts per batch
- Ingestion: 50 documents per batch
- Configurable via environment

### Indexes
- Keyword indexes: jiraKey, testCaseId, priority, etc.
- Array indexes: tags, platforms, relatedIssues
- Text indexes: title, action (for full-text search)

## Example Queries

### Localization Search
```
"Spanish localization on Team Page"
→ Finds tests with localization tags in both collections
```

### Live Game Search
```
"Live game MIG validations"
→ Matches live_state and requires_live_game tags
```

### Event-Specific Search
```
"Jewel event regressions"
→ Returns doc and step matches for jewel_event
```

## Future Enhancements

1. **MCP Wrapper**: For AI tool integration
2. **Incremental Updates**: Track changes over time
3. **Query Expansion**: Synonym and related term search
4. **Advanced Reranking**: ML-based result ordering
5. **Caching Layer**: For frequently accessed tests
6. **Analytics**: Search usage and performance metrics