# MLB QBench MCP Toolset Catalog

This document provides a comprehensive catalog of all tools exposed by the MLB QBench Model Context Protocol (MCP) server. These tools enable AI assistants to interact with the test retrieval system for semantic search, data management, and service monitoring.

## Overview

The MLB QBench MCP server (`mlb-qbench`) exposes 5 tools for test discovery and management through semantic vector search. All tools communicate with the FastAPI backend service and require proper environment configuration.

## How to Use

For local setup and running instructions, see the [README](../README.md#quick-start). The MCP server can be started with:

```bash
make mcp-server
# or
python -m src.mcp
```

## Tools Summary

| Tool | Purpose | Inputs (Summary) | Outputs (Summary) | Notes |
|------|---------|------------------|-------------------|-------|
| [check_health](#check_health) | Monitor service health and collection statistics | None | Service status, Qdrant stats, embedder info | Rate limited: 60/min |
| [find_similar_tests](#find_similar_tests) | Find tests similar to a reference test | jira_key, top_k, scope | Ranked similar tests with scores | Uses vector similarity |
| [get_test_by_jira](#get_test_by_jira) | Direct test lookup by JIRA key | jira_key | Full test details with steps | Exact match only |
| [ingest_tests](#ingest_tests) | Trigger test data ingestion | functional_path, api_path | Ingestion statistics | Rate limited: 5/min |
| [search_tests](#search_tests) | Semantic search with optional filters | query, top_k, filters | Ranked test results | Hybrid search algorithm |

## Tool Details

### check_health

Check the health status and statistics of the QBench service, including Qdrant vector database connectivity and collection metrics.

#### Inputs

| Property | Type | Required | Description | Allowed Values |
|----------|------|----------|-------------|----------------|
| *(none)* | - | - | No input parameters required | - |

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| status | string | Overall service health status (HEALTHY/DEGRADED/UNHEALTHY) |
| qdrant.status | string | Qdrant connection status |
| qdrant.collections | object | Collection names with point counts |
| embedder.provider | string | Active embedding provider name |
| embedder.model | string | Active embedding model name |

#### Preconditions & Permissions

- **Environment Variables**: 
  - `API_BASE_URL` (default: http://localhost:8000)
  - `API_KEY` or `MASTER_API_KEY` (optional for authentication)
- **Services Required**: FastAPI server must be running

#### Failure Modes

- HTTP 503: Service unavailable (Qdrant not connected)
- HTTP 401: Invalid or missing API key (if authentication enabled)
- Connection timeout: API server not reachable

#### Example

~~~json
// MCP tool invocation
{
  "tool": "check_health",
  "input": {}
}

// Sample response
"**Service Health: HEALTHY**

**Qdrant Collections:**
- test_docs: 1523 points
- test_steps: 4892 points

**Embedder:**
- Provider: openai
- Model: text-embedding-3-large"
~~~

### find_similar_tests

Find tests that are semantically similar to a reference test identified by its JIRA key.

#### Inputs

| Property | Type | Required | Description | Allowed Values |
|----------|------|----------|-------------|----------------|
| jira_key | string | Yes | JIRA key of the reference test | e.g., "FRAMED-1390" |
| top_k | integer | No | Number of similar tests to return | Default: 10, Max: 100 |
| scope | string | No | Search scope for similarity | "docs", "steps", "all" (default: "all") |

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| results | array | List of similar tests ordered by similarity score |
| results[].test | object | Test metadata (uid, title, tags, priority) |
| results[].score | float | Similarity score (0.0 to 1.0, higher is more similar) |

#### Preconditions & Permissions

- **Environment Variables**:
  - `API_BASE_URL` (default: http://localhost:8000)
  - `API_KEY` or `MASTER_API_KEY` (optional)
- **Data Requirements**: Reference test must exist in the database

#### Failure Modes

- HTTP 404: Reference test not found with given JIRA key
- HTTP 400: Invalid scope parameter
- Empty results: No similar tests found (not an error)

#### Example

~~~json
// MCP tool invocation
{
  "tool": "find_similar_tests",
  "input": {
    "jira_key": "FRAMED-1390",
    "top_k": 5,
    "scope": "all"
  }
}

// Sample response
"**Tests similar to FRAMED-1390:**

1. **User Login with Valid Credentials**
   - UID: FRAMED-1391
   - Similarity Score: 0.923
   - Tags: login, authentication, web

2. **Mobile App Login Flow**
   - UID: FRAMED-2456
   - Similarity Score: 0.891
   - Tags: login, mobile, ios"
~~~

### get_test_by_jira

Retrieve complete test details for a specific test identified by its JIRA key.

#### Inputs

| Property | Type | Required | Description | Allowed Values |
|----------|------|----------|-------------|----------------|
| jira_key | string | Yes | JIRA key to lookup | e.g., "FRAMED-1390", "API-5678" |

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| uid | string | Unique test identifier |
| title | string | Test title/summary |
| jiraKey | string | JIRA issue key |
| priority | string | Test priority level |
| tags | array[string] | Associated tags/labels |
| platforms | array[string] | Target platforms |
| summary | string | Detailed test description |
| steps | array[object] | Test execution steps |
| steps[].index | integer | Step sequence number |
| steps[].action | string | Step action description |
| steps[].expected | array[string] | Expected results |

#### Preconditions & Permissions

- **Environment Variables**:
  - `API_BASE_URL` (default: http://localhost:8000)
  - `API_KEY` or `MASTER_API_KEY` (optional)
- **Data Requirements**: Test with specified JIRA key must exist

#### Failure Modes

- HTTP 404: Test not found with given JIRA key
- HTTP 400: Invalid JIRA key format

#### Example

~~~json
// MCP tool invocation
{
  "tool": "get_test_by_jira",
  "input": {
    "jira_key": "FRAMED-1390"
  }
}

// Sample response
"**Login functionality test**

- UID: tc_func_001
- JIRA Key: FRAMED-1390
- Priority: High
- Tags: login, authentication, web
- Platforms: iOS, Android, Web

**Summary:**
Verify user can log in with valid credentials

**Steps (2):**
1. Navigate to login page
   Expected: Login page displays correctly
2. Enter valid username and password
   Expected: Credentials accepted, user logged in"
~~~

### ingest_tests

Trigger ingestion of test data from JSON files into the vector database. Supports both functional and API test formats.

#### Inputs

| Property | Type | Required | Description | Allowed Values |
|----------|------|----------|-------------|----------------|
| functional_path | string | No | Path to functional tests JSON file | Absolute or relative file path |
| api_path | string | No | Path to API tests JSON file | Absolute or relative file path |

*Note: At least one path should be provided. If no paths are specified, will attempt default paths from data/ directory.*

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| functional | object | Functional test ingestion results |
| functional.docs_ingested | integer | Number of test documents ingested |
| functional.steps_ingested | integer | Number of test steps ingested |
| api | object | API test ingestion results |
| api.docs_ingested | integer | Number of test documents ingested |
| api.steps_ingested | integer | Number of test steps ingested |

#### Preconditions & Permissions

- **Environment Variables**:
  - `API_BASE_URL` (default: http://localhost:8000)
  - `API_KEY` or `MASTER_API_KEY` (recommended for ingestion)
  - `EMBED_PROVIDER` and associated API keys (OpenAI, Cohere, etc.)
- **File Access**: JSON files must be accessible from the API server
- **Rate Limiting**: 5 requests per minute

#### Failure Modes

- HTTP 404: File not found at specified path
- HTTP 400: Invalid JSON format or missing required fields
- HTTP 429: Rate limit exceeded
- HTTP 500: Embedding API failure or Qdrant connection error

#### Example

~~~json
// MCP tool invocation
{
  "tool": "ingest_tests",
  "input": {
    "functional_path": "data/functional_tests_normalized.json",
    "api_path": "data/api_tests_normalized.json"
  }
}

// Sample response
"**Ingestion Complete**

- Functional Tests: 523 docs, 1847 steps
- API Tests: 198 docs, 592 steps"
~~~

### search_tests

Perform semantic search for tests using natural language queries with optional filtering.

#### Inputs

| Property | Type | Required | Description | Allowed Values |
|----------|------|----------|-------------|----------------|
| query | string | Yes | Natural language search query | Any text |
| top_k | integer | No | Maximum results to return | Default: 20, Max: 100 |
| filters | object | No | Optional filter criteria | See filter properties below |
| filters.tags | array[string] | No | Filter by tags | e.g., ["login", "api"] |
| filters.priority | string | No | Filter by priority level | "Critical", "High", "Medium", "Low" |
| filters.platforms | array[string] | No | Filter by platforms | e.g., ["iOS", "Android", "Web"] |
| filters.folderStructure | array[string] | No | Filter by folder paths | e.g., ["API Tests/Auth"] |
| filters.testType | string | No | Filter by test type | e.g., "Manual", "API", "Automated" |
| filters.relatedIssues | array[string] | No | Filter by related JIRA issues | e.g., ["FRAMED-123"] |
| filters.testPath | string | No | Filter by test file path pattern | e.g., "tests/api/*" |

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| results | array | Ranked list of matching tests |
| results[].test | object | Test metadata (uid, title, priority, tags, summary) |
| results[].score | float | Relevance score (0.0 to 1.0) |
| results[].matched_steps | string | Comma-separated list of matched step indices |

#### Preconditions & Permissions

- **Environment Variables**:
  - `API_BASE_URL` (default: http://localhost:8000)
  - `API_KEY` or `MASTER_API_KEY` (optional)
  - Embedding provider configured and accessible
- **Services Required**: Qdrant must be running with indexed data
- **Rate Limiting**: 60 requests per minute

#### Failure Modes

- HTTP 400: Invalid filter parameters
- HTTP 429: Rate limit exceeded
- HTTP 503: Qdrant or embedding service unavailable
- Empty results: No tests match the query (not an error)

#### Example

~~~json
// MCP tool invocation
{
  "tool": "search_tests",
  "input": {
    "query": "user authentication login flow",
    "top_k": 10,
    "filters": {
      "priority": "High",
      "platforms": ["iOS", "Android"],
      "tags": ["authentication"]
    }
  }
}

// Sample response
"**1. Login functionality test**
- UID: tc_func_001
- Priority: High
- Tags: login, authentication, web
- Score: 0.892
- Matched Steps: 1,2
- Summary: Verify user can log in with valid credentials...

**2. Mobile App Authentication**
- UID: tc_api_045
- Priority: High
- Tags: api, authentication, mobile
- Score: 0.847
- Summary: Test OAuth2 authentication flow for mobile apps..."
~~~

## Change Log for Tools

Tool definitions are maintained in `src/mcp/server.py`. For version history and changes, see the main project [releases](https://github.com/your-repo/releases).

## See Also

- [MCP Usage Guide](MCP_USAGE.md) - Setup and configuration instructions
- [API Documentation](API_DOCUMENTATION.md) - REST API endpoints reference
- [README](../README.md) - Project overview and quick start