# MCP Tools Reference Guide

This guide provides detailed documentation for all tools available through the MLB QBench MCP server, including usage patterns, parameters, and examples for AI assistants like Claude.

## Table of Contents

1. [Overview](#overview)
2. [Setup & Configuration](#setup--configuration)
3. [Available Tools](#available-tools)
   - [search_tests](#search_tests)
   - [get_test_by_jira](#get_test_by_jira)
   - [find_similar_tests](#find_similar_tests)
   - [ingest_tests](#ingest_tests)
   - [check_health](#check_health)
4. [Usage Patterns](#usage-patterns)
5. [Response Formats](#response-formats)
6. [Error Handling](#error-handling)
7. [Best Practices](#best-practices)

## Overview

The MCP (Model Context Protocol) server exposes MLB QBench functionality as tools that AI assistants can use to interact with the test retrieval system. These tools enable natural language queries and seamless integration with AI workflows.

### Key Capabilities

- **Semantic Search**: Find tests using natural language queries
- **Direct Lookup**: Retrieve specific tests by JIRA key
- **Similarity Search**: Find tests similar to a reference test
- **Data Management**: Trigger test data ingestion
- **Health Monitoring**: Check service status and statistics

## Setup & Configuration

### For Claude Desktop

1. **Locate configuration file**:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add MCP server configuration**:
   ```json
   {
     "mcpServers": {
       "mlb-qbench": {
         "command": "python",
         "args": ["-m", "src.mcp"],
         "cwd": "/path/to/mlb-qbench",
         "env": {
           "API_BASE_URL": "http://localhost:8000",
           "PYTHONPATH": "/path/to/mlb-qbench"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** to load the configuration

### Verifying Connection

Ask Claude: "Can you check if the QBench service is healthy?"

If configured correctly, Claude will use the `check_health` tool automatically.

## Available Tools

### search_tests

Performs semantic search across all test documents and steps with optional filtering.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `query` | string | Yes | Natural language search query | "Spanish localization on Team Page" |
| `top_k` | integer | No | Number of results to return (default: 20) | 10 |
| `filters` | object | No | Filter criteria object | See below |

#### Filters Object

```json
{
  "tags": ["api", "localization"],
  "priority": "High",
  "platforms": ["web", "mobile"],
  "folderStructure": ["Web", "Team"],
  "testType": "functional",
  "relatedIssues": ["BUG-123"],
  "testPath": "tests/api/"
}
```

#### Example Usage

**Natural Language Request**:
```
"Find all API tests related to team page localization with high priority"
```

**Claude's Tool Call**:
```json
{
  "tool": "search_tests",
  "arguments": {
    "query": "team page localization",
    "top_k": 20,
    "filters": {
      "tags": ["api"],
      "priority": "High"
    }
  }
}
```

#### Response Format

```markdown
**1. English Language - Team Page API**
- UID: FRAMED-1390
- Priority: High
- Tags: team_page, api, localization
- Score: 0.892
- Matched Steps: 2

**2. Spanish Language - Team Page API**
- UID: FRAMED-1391
- Priority: High
- Tags: team_page, api, localization, spanish
- Score: 0.875
```

### get_test_by_jira

Retrieves complete test details for a specific JIRA key.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `jira_key` | string | Yes | JIRA issue key | "FRAMED-1390" |

#### Example Usage

**Natural Language Request**:
```
"Show me the details for test FRAMED-1390"
```

**Claude's Tool Call**:
```json
{
  "tool": "get_test_by_jira",
  "arguments": {
    "jira_key": "FRAMED-1390"
  }
}
```

#### Response Format

```markdown
**English Language - Team Page API**

- UID: FRAMED-1390
- JIRA Key: FRAMED-1390
- Priority: High
- Tags: team_page, api, localization
- Platforms: web, mobile

**Summary:**
Validates English language content on the team page API endpoint

**Steps (5):**
1. Send GET request to /api/team/{teamId}
   Expected: 200 OK status
2. Verify response contains team name in English
   Expected: Team name matches expected value
3. Check player names are in English format
   Expected: First name, Last name order
... and 2 more steps
```

### find_similar_tests

Finds tests similar to a reference test based on semantic similarity.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `jira_key` | string | Yes | Reference test JIRA key | "FRAMED-643" |
| `top_k` | integer | No | Number of results (default: 10) | 5 |
| `scope` | string | No | Search scope: "docs", "steps", or "all" (default: "all") | "docs" |

#### Example Usage

**Natural Language Request**:
```
"Find 5 tests similar to FRAMED-643, focusing on document content"
```

**Claude's Tool Call**:
```json
{
  "tool": "find_similar_tests",
  "arguments": {
    "jira_key": "FRAMED-643",
    "top_k": 5,
    "scope": "docs"
  }
}
```

#### Response Format

```markdown
**Tests similar to FRAMED-643:**

1. **Player Statistics - Season View**
   - UID: FRAMED-645
   - Similarity Score: 0.892
   - Tags: statistics, player, season

2. **Player Statistics - Career View**
   - UID: FRAMED-712
   - Similarity Score: 0.845
   - Tags: statistics, player, career

3. **Team Statistics Dashboard**
   - UID: API-234
   - Similarity Score: 0.823
   - Tags: statistics, team, dashboard
```

### ingest_tests

Triggers ingestion of test data from JSON files.

#### Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `functional_path` | string | No | Path to functional tests JSON | "data/functional_tests_xray.json" |
| `api_path` | string | No | Path to API tests JSON | "data/api_tests_xray.json" |

**Note**: At least one path must be provided.

#### Example Usage

**Natural Language Request**:
```
"Ingest the functional tests from data/functional_tests_xray.json"
```

**Claude's Tool Call**:
```json
{
  "tool": "ingest_tests",
  "arguments": {
    "functional_path": "data/functional_tests_xray.json"
  }
}
```

#### Response Format

```markdown
**Ingestion Complete**

- Functional Tests: 150 docs, 832 steps
```

### check_health

Checks the health status of the QBench service and its dependencies.

#### Parameters

None required.

#### Example Usage

**Natural Language Request**:
```
"Is the QBench service healthy?"
```

**Claude's Tool Call**:
```json
{
  "tool": "check_health",
  "arguments": {}
}
```

#### Response Format

```markdown
**Service Health: HEALTHY**

**Qdrant Collections:**
- test_docs: 1,245 points
- test_steps: 6,832 points

**Embedder:**
- Provider: openai
- Model: text-embedding-3-large
```

## Usage Patterns

### Complex Queries

**User**: "I need to find all high-priority API tests related to live game features that have been updated in the last month"

**Claude's Approach**:
```json
{
  "tool": "search_tests",
  "arguments": {
    "query": "live game features",
    "filters": {
      "priority": "High",
      "tags": ["api"],
      "testType": "api"
    }
  }
}
```

### Multi-Step Workflows

**User**: "Find tests similar to FRAMED-1390 and then check if any of them are related to localization"

**Claude's Workflow**:
1. First, find similar tests:
   ```json
   {
     "tool": "find_similar_tests",
     "arguments": {
       "jira_key": "FRAMED-1390",
       "top_k": 10
     }
   }
   ```

2. Then search for localization within results:
   ```json
   {
     "tool": "search_tests",
     "arguments": {
       "query": "localization",
       "filters": {
         "tags": ["localization"]
       }
     }
   }
   ```

### Exploratory Analysis

**User**: "What kind of tests do we have in the system?"

**Claude's Approach**:
1. Check system health for statistics
2. Run broad searches with different filters
3. Summarize findings

## Response Formats

### Success Responses

All successful responses return formatted markdown text suitable for display in chat interfaces:

- **Headers** for test titles
- **Bullet points** for metadata
- **Numbered lists** for ranked results
- **Emphasis** for important information

### Error Responses

```markdown
API Error (404): Test with JIRA key INVALID-123 not found
```

Common error codes:
- `400`: Invalid request parameters
- `404`: Resource not found
- `500`: Server error
- `503`: Service unavailable

## Error Handling

### Common Scenarios

1. **Service Unavailable**
   - Error: "Connection refused"
   - Solution: Ensure QBench API is running on specified port

2. **Invalid Parameters**
   - Error: "Invalid filter field: 'invalidField'"
   - Solution: Check parameter names against documentation

3. **No Results**
   - Response: "No tests found matching your query"
   - Solution: Broaden search criteria or check data ingestion

### Debugging Tips

1. **Enable verbose logging**:
   ```bash
   LOG_LEVEL=DEBUG python -m src.mcp
   ```

2. **Test API directly**:
   ```bash
   curl http://localhost:8000/healthz
   ```

3. **Check MCP server logs**:
   - Look for connection errors
   - Verify tool execution traces

## Best Practices

### 1. Query Construction

- **Be specific**: "team page API tests" vs just "tests"
- **Use filters**: Narrow results with appropriate filters
- **Combine terms**: "localization spanish team page"

### 2. Filter Usage

- **Start broad**: Begin without filters, then narrow
- **Layer filters**: Add one filter at a time
- **Use arrays**: Tags and platforms accept multiple values

### 3. Performance

- **Limit results**: Use appropriate `top_k` values
- **Scope searches**: Use `scope` parameter for similarity
- **Batch operations**: Combine related queries when possible

### 4. Natural Language

The MCP server is designed for natural language interaction:

✅ **Good**: "Find all high-priority API tests for team features"
❌ **Avoid**: "search_tests query='team' filters={'priority':'High'}"

### 5. Context Awareness

Claude maintains context across tool calls:

```
User: "Find tests for the team page"
Claude: [Uses search_tests tool]

User: "Now show me the first one in detail"
Claude: [Uses get_test_by_jira with the first result's key]
```

## Advanced Usage

### Combining Tools

```python
# Pseudo-workflow for comprehensive analysis
1. check_health() → Get system statistics
2. search_tests(query="", top_k=100) → Sample of all tests
3. Extract unique tags/priorities → Understand data landscape
4. search_tests(filters={...}) → Targeted searches
5. find_similar_tests() → Explore relationships
```

### Custom Workflows

AI assistants can create sophisticated workflows:

1. **Test Coverage Analysis**: Search across different categories
2. **Regression Suite Building**: Find related tests by similarity
3. **Impact Analysis**: Identify tests affected by changes
4. **Test Prioritization**: Filter and rank by multiple criteria

## Summary

The MCP tools provide a natural interface for AI assistants to:
- Search and retrieve test information
- Analyze test relationships
- Manage test data
- Monitor system health

By following these patterns and best practices, AI assistants can effectively help users navigate and utilize the MLB QBench test retrieval system.