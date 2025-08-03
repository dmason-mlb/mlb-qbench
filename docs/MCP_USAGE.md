# MCP (Model Context Protocol) Integration

MLB QBench includes an MCP server that allows AI assistants to interact with the test retrieval service using natural language.

## Overview

The MCP server exposes the QBench functionality as tools that AI assistants can use to:
- Search for tests using semantic queries
- Retrieve tests by JIRA key
- Find similar tests
- Trigger data ingestion
- Check service health

## Installation

The MCP server is included in the main package. Make sure you have installed the project with MCP support:

```bash
pip install -e .
```

## Usage

### Running the MCP Server

You can run the MCP server in several ways:

1. **Direct execution**:
   ```bash
   python -m src.mcp
   ```

2. **With custom API URL**:
   ```bash
   API_BASE_URL=http://localhost:8000 python -m src.mcp
   ```

### Configuring Claude Desktop

To use the MCP server with Claude Desktop, add the following to your Claude configuration:

1. Open Claude Desktop settings
2. Go to the Developer section
3. Add the following MCP server configuration:

```json
{
  "mcpServers": {
    "mlb-qbench": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "env": {
        "API_BASE_URL": "http://localhost:8000",
        "API_KEY": "your-api-key-here",
        "PYTHONPATH": "/path/to/mlb-qbench"
      }
    }
  }
}
```

Make sure to:
- Update the `PYTHONPATH` to point to your mlb-qbench directory
- Ensure the QBench API is running on the specified `API_BASE_URL`
- **Important**: Set the `API_KEY` to match one of the keys configured in your `.env` file:
  - Either use the value from `MASTER_API_KEY`
  - Or use one of the comma-separated values from `API_KEYS`
  - Without a valid API key, all search requests will fail with 401 errors

## Available Tools

### search_tests

Search for tests using semantic search with optional filters.

**Parameters:**
- `query` (required): Search query text
- `top_k` (optional): Number of results to return (default: 20)
- `filters` (optional): Object with filter criteria
  - `tags`: Array of tags to filter by
  - `priority`: Priority level (Critical, High, Medium, Low)
  - `platforms`: Array of platforms
  - `folderStructure`: Array of folder paths
  - `testType`: Test type string
  - `relatedIssues`: Array of issue IDs
  - `testPath`: Test path pattern

**Example:**
```
"Search for Spanish localization tests on the team page with high priority"
```

### get_test_by_jira

Retrieve a specific test by its JIRA key.

**Parameters:**
- `jira_key` (required): JIRA key (e.g., "FRAMED-1390")

**Example:**
```
"Get the test details for FRAMED-1390"
```

### find_similar_tests

Find tests similar to a given test.

**Parameters:**
- `jira_key` (required): Reference test JIRA key
- `top_k` (optional): Number of results (default: 10)
- `scope` (optional): Search scope - "docs", "steps", or "all" (default: "all")

**Example:**
```
"Find 5 tests similar to FRAMED-643 focusing on document content"
```

### ingest_tests

Trigger ingestion of test data from JSON files.

**Parameters:**
- `functional_path` (optional): Path to functional tests JSON
- `api_path` (optional): Path to API tests JSON

**Example:**
```
"Ingest the functional tests from data/functional_tests_xray.json"
```

### check_health

Check the health status of the QBench service.

**No parameters required**

**Example:**
```
"Check if the QBench service is healthy"
```

## Example Conversations

### Finding Tests

```
User: "I need to find all tests related to live game validations"
Assistant: I'll search for tests related to live game validations.

[Calls search_tests with query="Live game MIG validations"]

I found 15 tests related to live game validations. Here are the top results:
1. Live Game MIG Validation - Basic Flow (FRAMED-892)
2. Live State Update During Active Game (FRAMED-1023)
3. MIG Data Refresh - Live Context (API-445)
...
```

### Getting Test Details

```
User: "Show me the details for test FRAMED-1390"
Assistant: I'll retrieve the test details for FRAMED-1390.

[Calls get_test_by_jira with jira_key="FRAMED-1390"]

Here are the details for FRAMED-1390:
- Title: English Language - Team Page API
- Priority: High
- Tags: team_page, api, localization
- Summary: Validates English language content on the team page API endpoint
- Steps: 5 test steps including GET request validation and response checks
```

### Finding Similar Tests

```
User: "Find tests similar to FRAMED-643"
Assistant: I'll find tests similar to FRAMED-643.

[Calls find_similar_tests with jira_key="FRAMED-643"]

I found several tests similar to FRAMED-643:
1. FRAMED-645 - Similar localization flow (similarity: 0.892)
2. FRAMED-712 - Related API validation (similarity: 0.845)
3. API-234 - Same component testing (similarity: 0.823)
```

## Troubleshooting

### Common Issues

1. **MCP server not found**
   - Ensure the Python path includes the mlb-qbench directory
   - Verify the package is installed: `pip list | grep mlb-qbench`

2. **Connection refused**
   - Check that the QBench API is running: `curl http://localhost:8000/healthz`
   - Verify the API_BASE_URL matches your service location

3. **No results returned**
   - Ensure data has been ingested into Qdrant
   - Check the collections have data: `curl http://localhost:6533/collections`

### Debug Mode

To run the MCP server with debug logging:

```bash
LOG_LEVEL=DEBUG python -m src.mcp
```

## Integration with Other AI Tools

The MCP server follows the Model Context Protocol standard and can be integrated with:
- Claude Desktop
- Continue.dev
- Any MCP-compatible AI assistant

For custom integrations, the server exposes standard MCP endpoints:
- `/tools` - List available tools
- `/tool/call` - Execute a tool

## Security Considerations

- The MCP server only has read access to the QBench API
- File paths in ingestion are validated against allowed directories
- No direct database access is provided
- API authentication can be added via environment variables