# MCP Server Enhancement Suggestions

This document outlines optional improvements that could enhance the MLB QBench MCP server functionality and developer experience.

## 1. Add Rate Limit Metadata to Tool Definitions

**Location:** `src/mcp/server.py`

**Enhancement:** Add explicit rate limit information to each tool's metadata so AI assistants can be aware of usage constraints.

**Implementation:**

```python
# In src/mcp/server.py, modify each tool definition to include rate limit metadata

types.Tool(
    name="search_tests",
    description="Search for tests using semantic search with optional filters",
    inputSchema={...},
    # Add this custom extension field:
    extensions={
        "x-rate-limit": {
            "requests": 60,
            "window": "1m",
            "scope": "global"
        }
    }
)

types.Tool(
    name="ingest_tests",
    description="Trigger ingestion of test data from JSON files",
    inputSchema={...},
    # Add this for the ingestion endpoint:
    extensions={
        "x-rate-limit": {
            "requests": 5,
            "window": "1m",
            "scope": "global"
        }
    }
)
```

**Benefits:**
- AI assistants can proactively manage request pacing
- Clearer API usage expectations
- Reduced chance of hitting rate limits during automated workflows

## 2. Add Stability and Version Tags

**Location:** `src/mcp/server.py`

**Enhancement:** Include stability indicators and version information for each tool.

**Implementation:**

```python
# In tool definitions, add stability and version metadata

types.Tool(
    name="search_tests",
    description="Search for tests using semantic search with optional filters",
    inputSchema={...},
    extensions={
        "x-stability": "stable",  # Options: "stable", "beta", "experimental", "deprecated"
        "x-version": "1.0.0",
        "x-since": "0.1.0",  # Version when tool was introduced
        "x-deprecation": None  # Or {"version": "2.0.0", "alternative": "search_tests_v2"}
    }
)
```

**Benefits:**
- Clear communication about tool maturity
- Easier deprecation management
- Version-aware tool usage by AI assistants

## 3. Add Batch Operations Tool

**Location:** `src/mcp/server.py`

**Enhancement:** Create a new tool for executing multiple operations in parallel, reducing round-trip latency.

**Implementation:**

```python
# Add to the tool list in handle_list_tools()

types.Tool(
    name="batch_operations",
    description="Execute multiple operations in parallel for improved performance",
    inputSchema={
        "type": "object",
        "properties": {
            "operations": {
                "type": "array",
                "description": "Array of operations to execute in parallel",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "description": "Unique identifier for this operation"
                        },
                        "tool": {
                            "type": "string",
                            "enum": ["search_tests", "get_test_by_jira", "find_similar_tests"],
                            "description": "Tool to execute"
                        },
                        "arguments": {
                            "type": "object",
                            "description": "Arguments for the tool"
                        }
                    },
                    "required": ["id", "tool", "arguments"]
                },
                "maxItems": 10  # Limit parallel operations
            },
            "continue_on_error": {
                "type": "boolean",
                "description": "Whether to continue if an operation fails",
                "default": True
            }
        },
        "required": ["operations"]
    }
)

# In handle_call_tool(), add handler:

elif name == "batch_operations":
    operations = arguments["operations"]
    continue_on_error = arguments.get("continue_on_error", True)
    
    # Execute operations in parallel
    tasks = []
    for op in operations:
        tasks.append(
            handle_single_operation(
                op["tool"], 
                op["arguments"],
                op["id"]
            )
        )
    
    results = await asyncio.gather(*tasks, return_exceptions=continue_on_error)
    
    # Format batch results
    batch_results = []
    for i, (op, result) in enumerate(zip(operations, results)):
        if isinstance(result, Exception) and continue_on_error:
            batch_results.append({
                "id": op["id"],
                "status": "error",
                "error": str(result)
            })
        else:
            batch_results.append({
                "id": op["id"],
                "status": "success",
                "result": result
            })
    
    return [types.TextContent(
        type="text",
        text=json.dumps(batch_results, indent=2)
    )]
```

**Benefits:**
- Significantly reduced latency for multiple operations
- Better performance for complex workflows
- Atomic batch processing capabilities

## 4. Add Query Validation Tool

**Location:** `src/mcp/server.py`

**Enhancement:** Add a tool to validate and optimize search queries before execution.

**Implementation:**

```python
types.Tool(
    name="validate_query",
    description="Validate and optimize a search query before execution",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Query to validate"
            },
            "filters": {
                "type": "object",
                "description": "Filters to validate"
            },
            "suggest_improvements": {
                "type": "boolean",
                "description": "Whether to suggest query improvements",
                "default": True
            }
        },
        "required": ["query"]
    }
)
```

**Benefits:**
- Catch errors before expensive search operations
- Query optimization suggestions
- Better user experience with guided query construction

## 5. Add Streaming Support for Large Results

**Location:** `src/mcp/server.py`

**Enhancement:** Implement streaming for tools that return large datasets.

**Implementation:**

```python
# Add a streaming variant of search_tests

types.Tool(
    name="search_tests_stream",
    description="Search with streaming results for large datasets",
    inputSchema={
        # Same as search_tests, plus:
        "properties": {
            # ... existing properties ...
            "stream_config": {
                "type": "object",
                "properties": {
                    "chunk_size": {
                        "type": "integer",
                        "description": "Results per chunk",
                        "default": 10
                    },
                    "max_chunks": {
                        "type": "integer",
                        "description": "Maximum chunks to return",
                        "default": 10
                    }
                }
            }
        }
    }
)
```

**Benefits:**
- Better handling of large result sets
- Reduced memory footprint
- Progressive result delivery

## 6. Add Caching Headers

**Location:** `src/mcp/server.py`

**Enhancement:** Include cache control information in responses.

**Implementation:**

```python
# In handle_call_tool responses, add cache metadata

return [types.TextContent(
    type="text",
    text=result_text,
    metadata={
        "cache_control": {
            "max_age": 300,  # 5 minutes for search results
            "etag": hashlib.md5(result_text.encode()).hexdigest(),
            "vary": ["query", "filters"]
        }
    }
)]
```

**Benefits:**
- Reduced API calls for repeated queries
- Better performance for frequently accessed data
- Lower embedding API costs

## 7. Add Tool Usage Analytics

**Location:** `src/mcp/server.py`

**Enhancement:** Track tool usage patterns for optimization.

**Implementation:**

```python
# Add a simple analytics collector

from collections import defaultdict
from datetime import datetime

class ToolAnalytics:
    def __init__(self):
        self.usage_count = defaultdict(int)
        self.error_count = defaultdict(int)
        self.latency_sum = defaultdict(float)
        self.last_used = {}
    
    def record_usage(self, tool_name: str, latency: float, success: bool):
        self.usage_count[tool_name] += 1
        self.latency_sum[tool_name] += latency
        self.last_used[tool_name] = datetime.now()
        if not success:
            self.error_count[tool_name] += 1
    
    def get_stats(self):
        return {
            tool: {
                "usage_count": self.usage_count[tool],
                "error_rate": self.error_count[tool] / max(1, self.usage_count[tool]),
                "avg_latency": self.latency_sum[tool] / max(1, self.usage_count[tool]),
                "last_used": self.last_used.get(tool)
            }
            for tool in self.usage_count
        }

# Initialize at module level
analytics = ToolAnalytics()

# Wrap handle_call_tool with analytics
async def handle_call_tool(...):
    start_time = time.time()
    success = False
    try:
        result = await _handle_call_tool_impl(...)
        success = True
        return result
    finally:
        latency = time.time() - start_time
        analytics.record_usage(name, latency, success)
```

**Benefits:**
- Identify most/least used tools
- Monitor performance trends
- Data-driven optimization decisions

## 8. Add Test Data Preview Tool

**Location:** `src/mcp/server.py`

**Enhancement:** Add a tool to preview test data before ingestion.

**Implementation:**

```python
types.Tool(
    name="preview_test_data",
    description="Preview and validate test data before ingestion",
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to test data file"
            },
            "sample_size": {
                "type": "integer",
                "description": "Number of tests to preview",
                "default": 5
            },
            "validate_only": {
                "type": "boolean",
                "description": "Only validate without preview",
                "default": False
            }
        },
        "required": ["file_path"]
    }
)
```

**Benefits:**
- Catch data issues before ingestion
- Preview data transformations
- Validate file formats and schemas

## Implementation Priority

1. **High Priority:**
   - Rate limit metadata (#1)
   - Batch operations (#3)
   - Query validation (#4)

2. **Medium Priority:**
   - Stability tags (#2)
   - Caching headers (#6)
   - Test data preview (#8)

3. **Low Priority:**
   - Streaming support (#5)
   - Usage analytics (#7)

## Testing Recommendations

For each enhancement:
1. Add unit tests in `tests/test_mcp_server.py`
2. Update integration tests for new tools
3. Add examples to TOOLSET.md documentation
4. Test with Claude Desktop or other MCP clients
5. Verify backward compatibility

## Notes

- All enhancements maintain backward compatibility
- Extensions use "x-" prefix following OpenAPI conventions
- Consider feature flags for gradual rollout
- Monitor performance impact of new features