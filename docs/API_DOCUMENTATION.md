# MLB QBench API Documentation

Complete API reference for the MLB QBench test retrieval service.

## Table of Contents

1. [Overview](#overview)
2. [Base URL & Authentication](#base-url--authentication)
3. [Endpoints](#endpoints)
   - [POST /search](#post-search)
   - [POST /ingest](#post-ingest)
   - [GET /by-jira/{key}](#get-by-jirakey)
   - [GET /similar/{key}](#get-similarkey)
   - [GET /healthz](#get-healthz)
4. [Request & Response Formats](#request--response-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)
7. [Examples](#examples)
8. [SDKs & Client Libraries](#sdks--client-libraries)

## Overview

The MLB QBench API provides RESTful endpoints for semantic search and retrieval of test cases. It leverages vector embeddings to enable natural language queries across test documentation and steps.

### Key Features

- **Semantic Search**: Natural language queries with vector similarity
- **Hybrid Search**: Combined document and step-level search
- **Filtering**: Multi-faceted filtering on metadata
- **Similarity**: Find related tests based on content
- **Idempotent Ingestion**: Safe data updates

## Base URL & Authentication

### Base URL
```
http://localhost:8000
```

### Authentication
All API endpoints require authentication using an API key in the `X-API-Key` header.

#### Setting up API Keys
1. Configure API keys in your `.env` file:
   ```bash
   MASTER_API_KEY=your-secure-master-key
   API_KEYS=client-key-1,client-key-2,client-key-3
   ```

2. Include the API key in all requests:
   ```http
   X-API-Key: your-api-key-here
   ```

### Required Headers
```http
Content-Type: application/json
Accept: application/json
X-API-Key: your-api-key-here
```

### Authentication Errors
Missing or invalid API keys return a 401 Unauthorized response:
```json
{
  "detail": "Missing API key"
}
```

## Endpoints

### POST /search

Performs semantic search across test documents and steps.

#### Request

```http
POST /search
Content-Type: application/json
```

#### Request Body

```json
{
  "query": "string",
  "top_k": 20,
  "filters": {
    "tags": ["string"],
    "priority": "High|Medium|Low|Critical",
    "platforms": ["string"],
    "folderStructure": ["string"],
    "testType": "string",
    "relatedIssues": ["string"],
    "testPath": "string"
  }
}
```

#### Parameters

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | Natural language search query |
| `top_k` | integer | No | 20 | Maximum number of results to return (1-100) |
| `filters` | object | No | {} | Filter criteria for narrowing results |

#### Filter Options

| Filter | Type | Description | Example |
|--------|------|-------------|---------|
| `tags` | string[] | Filter by test tags/labels | `["api", "regression"]` |
| `priority` | string | Filter by priority level | `"High"` |
| `platforms` | string[] | Filter by target platforms | `["web", "mobile"]` |
| `folderStructure` | string[] | Filter by folder hierarchy | `["Web", "Team"]` |
| `testType` | string | Filter by test type | `"functional"` |
| `relatedIssues` | string[] | Filter by related issue IDs | `["BUG-123"]` |
| `testPath` | string | Filter by test file path pattern | `"tests/api/"` |

#### Response

```json
[
  {
    "test": {
      "uid": "FRAMED-1390",
      "jiraKey": "FRAMED-1390",
      "title": "English Language - Team Page API",
      "priority": "High",
      "tags": ["team_page", "api", "localization"],
      "summary": "Validates English language content...",
      "steps": [...],
      "platforms": ["web", "mobile"],
      "folderStructure": ["Web", "Team", "Localization"],
      "updatedAt": "2024-01-15T10:30:00Z"
    },
    "score": 0.892,
    "matched_steps": [1, 3]
  }
]
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `test` | object | Complete test document |
| `score` | float | Similarity score (0-1) |
| `matched_steps` | integer[] | Step indices that matched the query |

#### Example

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "query": "Spanish localization on Team Page",
    "top_k": 10,
    "filters": {
      "tags": ["localization"],
      "priority": "High"
    }
  }'
```

### POST /ingest

Triggers ingestion of test data from JSON files.

#### Request

```http
POST /ingest
Content-Type: application/json
```

#### Request Body

```json
{
  "functional_path": "string",
  "api_path": "string"
}
```

#### Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `functional_path` | string | No* | Path to functional tests JSON file |
| `api_path` | string | No* | Path to API tests JSON file |

*At least one path must be provided.

#### Response

```json
{
  "status": "success",
  "functional": {
    "docs_ingested": 150,
    "steps_ingested": 832,
    "duration_seconds": 12.5
  },
  "api": {
    "docs_ingested": 75,
    "steps_ingested": 423,
    "duration_seconds": 6.3
  },
  "total_duration_seconds": 18.8
}
```

#### Example

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{
    "functional_path": "data/functional_tests_normalized.json",
    "api_path": "data/api_tests_normalized.json"
  }'
```

### GET /by-jira/{key}

Retrieves a specific test by its JIRA key.

#### Request

```http
GET /by-jira/{key}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | string | JIRA issue key (e.g., "FRAMED-1390") |

#### Response

```json
{
  "uid": "FRAMED-1390",
  "jiraKey": "FRAMED-1390",
  "testCaseId": "tc_1390",
  "title": "English Language - Team Page API",
  "priority": "High",
  "tags": ["team_page", "api", "localization"],
  "summary": "Validates English language content...",
  "steps": [
    {
      "index": 1,
      "action": "Send GET request to /api/team/{teamId}",
      "data": "teamId: 119",
      "expected": ["200 OK status"],
      "embedding_text": "Send GET request..."
    }
  ],
  "platforms": ["web", "mobile"],
  "folderStructure": ["Web", "Team", "Localization"],
  "testPath": "tests/api/team/localization.spec.js",
  "relatedIssues": ["BUG-2345", "STORY-123"],
  "updatedAt": "2024-01-15T10:30:00Z"
}
```

#### Error Response

```json
{
  "detail": "Test with JIRA key INVALID-123 not found"
}
```

#### Example

```bash
curl http://localhost:8000/by-jira/FRAMED-1390 \
  -H "X-API-Key: your-api-key-here"
```

### GET /similar/{key}

Finds tests similar to a given test.

#### Request

```http
GET /similar/{key}?top_k=10&scope=all
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `key` | string | Reference test JIRA key |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `top_k` | integer | 10 | Number of similar tests to return (1-50) |
| `scope` | string | "all" | Search scope: "docs", "steps", or "all" |

#### Scope Options

- `docs`: Search only in document-level vectors
- `steps`: Search only in step-level vectors
- `all`: Search in both collections and merge results

#### Response

```json
[
  {
    "test": {
      "uid": "FRAMED-1391",
      "jiraKey": "FRAMED-1391",
      "title": "Spanish Language - Team Page API",
      "priority": "High",
      "tags": ["team_page", "api", "localization", "spanish"],
      "summary": "Validates Spanish language content..."
    },
    "score": 0.945,
    "matched_steps": []
  }
]
```

#### Example

```bash
# Find 5 tests similar to FRAMED-1390, searching only documents
curl "http://localhost:8000/similar/FRAMED-1390?top_k=5&scope=docs" \
  -H "X-API-Key: your-api-key-here"
```

### GET /healthz

Health check endpoint for monitoring service status.

**Note**: The health check endpoint does not require authentication.

#### Request

```http
GET /healthz
```

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "0.1.0",
  "qdrant": {
    "status": "connected",
    "url": "http://localhost:6533",
    "collections": {
      "test_docs": {
        "status": "ready",
        "points_count": 1245,
        "segments_count": 1,
        "config": {
          "vector_size": 3072,
          "distance": "Cosine"
        }
      },
      "test_steps": {
        "status": "ready",
        "points_count": 6832,
        "segments_count": 1,
        "config": {
          "vector_size": 3072,
          "distance": "Cosine"
        }
      }
    }
  },
  "embedder": {
    "provider": "openai",
    "model": "text-embedding-3-large",
    "dimensions": 3072
  }
}
```

#### Health Status Values

- `healthy`: All systems operational
- `degraded`: Service operational but with issues
- `unhealthy`: Service not operational

#### Example

```bash
curl http://localhost:8000/healthz
```

## Request & Response Formats

### General Request Format

- **Content-Type**: `application/json`
- **Encoding**: UTF-8
- **Method**: As specified per endpoint

### General Response Format

- **Content-Type**: `application/json`
- **Encoding**: UTF-8
- **Status Codes**: Standard HTTP status codes

### Pagination

Currently, pagination is controlled by the `top_k` parameter. Future versions may implement cursor-based pagination:

```json
{
  "results": [...],
  "pagination": {
    "cursor": "eyJvZmZzZXQiOjIwfQ==",
    "has_more": true,
    "total_count": 156
  }
}
```

## Error Handling

### Error Response Format

```json
{
  "detail": "string",
  "status_code": 400,
  "type": "validation_error",
  "errors": [
    {
      "field": "query",
      "message": "Field required",
      "type": "missing"
    }
  ]
}
```

### Common Error Codes

| Status Code | Type | Description |
|-------------|------|-------------|
| 400 | `validation_error` | Invalid request parameters |
| 404 | `not_found` | Resource not found |
| 422 | `unprocessable_entity` | Valid JSON but semantic errors |
| 429 | `rate_limit_exceeded` | Too many requests |
| 500 | `internal_server_error` | Server error |
| 503 | `service_unavailable` | Service temporarily unavailable |

### Error Examples

#### Validation Error
```json
{
  "detail": "Invalid request parameters",
  "status_code": 400,
  "type": "validation_error",
  "errors": [
    {
      "field": "top_k",
      "message": "ensure this value is less than or equal to 100",
      "type": "value_error"
    }
  ]
}
```

#### Not Found Error
```json
{
  "detail": "Test with JIRA key INVALID-123 not found",
  "status_code": 404,
  "type": "not_found"
}
```

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Search endpoints** (`/search`, `/by-jira/*`, `/similar/*`): 60 requests per minute per IP
- **Ingestion endpoint** (`/ingest`): 5 requests per minute per IP
- **Health check** (`/healthz`): No rate limit

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1678886400
Retry-After: 60

{
  "detail": "Rate limit exceeded",
  "status_code": 429
}
```

## Examples

### Python

```python
import requests
import json

# Configure API key
API_KEY = "your-api-key-here"
BASE_URL = "http://localhost:8000"

# Search for tests
def search_tests(query, filters=None, api_key=API_KEY):
    url = f"{BASE_URL}/search"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key
    }
    payload = {
        "query": query,
        "top_k": 20,
        "filters": filters or {}
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Example usage
results = search_tests(
    "team page localization",
    filters={"priority": "High", "tags": ["api"]}
)

for result in results:
    print(f"{result['test']['title']} - Score: {result['score']:.3f}")
```

### JavaScript/TypeScript

```typescript
interface SearchRequest {
  query: string;
  top_k?: number;
  filters?: {
    tags?: string[];
    priority?: string;
    platforms?: string[];
  };
}

async function searchTests(request: SearchRequest, apiKey: string) {
  const response = await fetch('http://localhost:8000/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': apiKey,
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return await response.json();
}

// Example usage
const API_KEY = 'your-api-key-here';
const results = await searchTests({
  query: 'live game validations',
  top_k: 10,
  filters: {
    tags: ['live_state'],
    priority: 'High'
  }
}, API_KEY);
```

### cURL

```bash
# Set your API key
API_KEY="your-api-key-here"

# Search with complex filters
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "query": "player statistics API",
    "top_k": 15,
    "filters": {
      "tags": ["api", "statistics"],
      "priority": "High",
      "platforms": ["web", "mobile"],
      "folderStructure": ["API", "Player"]
    }
  }' | jq

# Get test by JIRA key
curl http://localhost:8000/by-jira/FRAMED-1390 \
  -H "X-API-Key: $API_KEY" | jq

# Find similar tests
curl "http://localhost:8000/similar/FRAMED-1390?top_k=5&scope=docs" \
  -H "X-API-Key: $API_KEY" | jq

# Check health (no API key required)
curl http://localhost:8000/healthz | jq
```

### HTTPie

```bash
# Set your API key
API_KEY="your-api-key-here"

# Search request
http POST localhost:8000/search \
  "X-API-Key:$API_KEY" \
  query="team page tests" \
  top_k=10 \
  filters:='{"priority": "High"}'

# Get by JIRA
http GET localhost:8000/by-jira/FRAMED-1390 \
  "X-API-Key:$API_KEY"

# Health check (no API key required)
http GET localhost:8000/healthz
```

## SDKs & Client Libraries

### OpenAPI Specification

The API provides an OpenAPI 3.0 specification at:

```
http://localhost:8000/openapi.json
```

View interactive documentation at:

```
http://localhost:8000/docs     # Swagger UI
http://localhost:8000/redoc    # ReDoc
```

### Generating Client Libraries

Use the OpenAPI spec to generate clients:

```bash
# Python client
openapi-generator generate -i http://localhost:8000/openapi.json \
  -g python -o ./mlb-qbench-python-client

# TypeScript client
openapi-generator generate -i http://localhost:8000/openapi.json \
  -g typescript-axios -o ./mlb-qbench-ts-client

# Go client
openapi-generator generate -i http://localhost:8000/openapi.json \
  -g go -o ./mlb-qbench-go-client
```

### Community SDKs

Currently, no official SDKs are provided. Community contributions are welcome!

## Performance Considerations

### Response Times

Typical response times under normal load:

- `/search`: 50-200ms (depends on result count)
- `/by-jira/{key}`: 10-30ms
- `/similar/{key}`: 100-300ms
- `/healthz`: 5-15ms
- `/ingest`: 10-60s (depends on data size)

### Optimization Tips

1. **Use filters**: Narrow searches to improve performance
2. **Limit results**: Use appropriate `top_k` values
3. **Cache responses**: Implement client-side caching
4. **Batch requests**: Combine multiple searches when possible

### Scaling

For production deployments:

1. **Horizontal scaling**: Deploy multiple API instances
2. **Load balancing**: Use nginx/HAProxy
3. **Caching layer**: Add Redis for frequent queries
4. **CDN**: Cache static responses
5. **Database optimization**: Tune Qdrant parameters

## Changelog

### Version 0.1.0 (Current)

- Initial release
- Basic search functionality
- JIRA lookup
- Similarity search
- Health monitoring
- Data ingestion

### Planned Features

- Webhook notifications for data updates
- Batch operations API
- GraphQL endpoint
- WebSocket support for real-time updates
- Advanced query language
- Test execution history