# MLB QBench MCP Toolset Catalog

This document provides a comprehensive catalog of all tools exposed by the MLB QBench Model Context Protocol (MCP) server. These tools enable AI assistants to interact with the test retrieval system for semantic search, data management, and service monitoring.

## Overview

The MLB QBench MCP server (`mlb-qbench-postgres`) exposes 4 tools for test discovery and management through semantic vector search using PostgreSQL+pgvector. All tools communicate directly with the PostgreSQL database and require proper environment configuration.

**Note**: The `ingest_tests` tool is currently not implemented in the PostgreSQL backend. See [TODO section](#todos) for planned functionality.

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
| [check_health](#check_health) | Monitor service health and database statistics | None | Service status, PostgreSQL stats, embedder info | Direct DB access |
| [find_similar_tests](#find_similar_tests) | Find tests similar to a reference test | uid, top_k | Ranked similar tests with scores | Uses vector similarity |
| [get_test_by_jira](#get_test_by_jira) | Direct test lookup by JIRA key | jira_key | Full test details with steps | Exact match only |
| [search_tests](#search_tests) | Semantic search with optional filters | query, top_k, filters | Ranked test results | Hybrid search algorithm |

## Tool Details

### check_health

Check the health status and statistics of the PostgreSQL QBench service, including database connectivity and collection metrics.

#### Inputs

| Property | Type | Required | Description | Allowed Values |
|----------|------|----------|-------------|----------------|
| *(none)* | - | - | No input parameters required | - |

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| status | string | Overall service health status (HEALTHY) |
| total_documents | integer | Total number of test documents in PostgreSQL |
| total_steps | integer | Total number of test steps in PostgreSQL |
| priority_distribution | object | Count of tests by priority level |
| test_type_distribution | object | Count of tests by test type |
| embedder.provider | string | Active embedding provider name |
| embedder.model | string | Active embedding model name |

#### Preconditions & Permissions

- **Environment Variables**: 
  - `DATABASE_URL` (PostgreSQL connection string)
  - `EMBED_PROVIDER` (default: openai)
  - `EMBED_MODEL` (default: text-embedding-3-small)
- **Services Required**: PostgreSQL with pgvector extension must be running

#### Failure Modes

- Database connection errors: PostgreSQL not available
- Missing environment variables: Required configuration not set
- pgvector extension not installed

#### Example

~~~json
// MCP tool invocation
{
  "tool": "check_health",
  "input": {}
}

// Sample response
"**Service Health: HEALTHY**

**PostgreSQL Database:**
- Status: Connected
- Total Documents: 104121
- Total Steps: 312363

**Priority Distribution:**
- High: 15423 tests
- Medium: 67890 tests
- Low: 20808 tests

**Test Type Distribution:**
- Manual: 89567 tests
- API: 14554 tests

**Embedder:**
- Provider: openai
- Model: text-embedding-3-small"
~~~

### find_similar_tests

Find tests that are semantically similar to a reference test identified by its UID.

#### Inputs

| Property | Type | Required | Description | Allowed Values |
|----------|------|----------|-------------|----------------|
| uid | string | Yes | UID of the reference test | e.g., "tc_func_001" |
| top_k | integer | No | Number of similar tests to return | Default: 10, Max: 100 |

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| results | array | List of similar tests ordered by similarity score |
| results[].uid | string | Test unique identifier |
| results[].title | string | Test title |
| results[].jira_key | string | JIRA key if available |
| results[].similarity | float | Similarity score (0.0 to 1.0, higher is more similar) |
| results[].tags | array[string] | Associated tags/labels |

#### Preconditions & Permissions

- **Environment Variables**:
  - `DATABASE_URL` (PostgreSQL connection string)
  - `EMBED_PROVIDER` and associated API keys (OpenAI, Cohere, etc.)
- **Data Requirements**: Reference test must exist in the database

#### Failure Modes

- Test not found: Reference UID doesn't exist in database
- Database connection error: PostgreSQL unavailable
- Empty results: No similar tests found (not an error)

#### Example

~~~json
// MCP tool invocation
{
  "tool": "find_similar_tests",
  "input": {
    "uid": "tc_func_001",
    "top_k": 5
  }
}

// Sample response
"**Tests similar to tc_func_001:**

1. **User Login with Valid Credentials**
   - UID: tc_func_002
   - JIRA Key: FRAMED-1391
   - Similarity: 0.923
   - Tags: login, authentication, web

2. **Mobile App Login Flow**
   - UID: tc_mobile_456
   - JIRA Key: FRAMED-2456
   - Similarity: 0.891
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
| jira_key | string | JIRA issue key |
| priority | string | Test priority level |
| tags | array[string] | Associated tags/labels |
| platforms | array[string] | Target platforms |
| test_type | string | Type of test (Manual, API, etc.) |
| summary | string | Detailed test description |
| description | string | Additional test description |
| steps | array[object] | Test execution steps |
| steps[].index | integer | Step sequence number |
| steps[].action | string | Step action description |
| steps[].expected | array[string] | Expected results |

#### Preconditions & Permissions

- **Environment Variables**:
  - `DATABASE_URL` (PostgreSQL connection string)
- **Data Requirements**: Test with specified JIRA key must exist

#### Failure Modes

- HTTP 404: Test not found with given JIRA key
- Database connection error: PostgreSQL unavailable

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
- Test Type: Manual

**Summary:**
Verify user can log in with valid credentials

**Description:**
This test validates the complete authentication flow including form validation, server communication, and successful redirection after login...

**Steps (2):**
1. Navigate to login page
   Expected: Login page displays correctly
2. Enter valid username and password
   Expected: Credentials accepted, user logged in"
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

#### Outputs

| Field | Type | Description |
|-------|------|-------------|
| results | array | Ranked list of matching tests |
| results[].uid | string | Test unique identifier |
| results[].title | string | Test title |
| results[].jira_key | string | JIRA key if available |
| results[].priority | string | Test priority level |
| results[].tags | array[string] | Associated tags/labels |
| results[].similarity | float | Relevance score (0.0 to 1.0) |
| results[].matched_steps | array | List of matched step objects |
| results[].summary | string | Test summary (truncated to 200 chars) |

#### Preconditions & Permissions

- **Environment Variables**:
  - `DATABASE_URL` (PostgreSQL connection string)
  - `EMBED_PROVIDER` and associated API keys
- **Services Required**: PostgreSQL with pgvector must be running with indexed data

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