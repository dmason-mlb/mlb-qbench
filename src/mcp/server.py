"""Model Context Protocol (MCP) server for MLB QBench test retrieval service.

This module implements a comprehensive MCP server that exposes MLB QBench's test search
and management capabilities as AI-compatible tools. The server provides semantic search,
test retrieval, similarity analysis, and data ingestion operations through a standardized
MCP interface for integration with AI assistants and development tools.

MCP Architecture:
    - Tool Registration: Defines available tools with JSON schema validation
    - Request Handling: Processes tool calls with async HTTP client operations
    - Response Formatting: Converts API responses to human-readable markdown
    - Error Management: Comprehensive error handling with detailed status reporting
    - Authentication: Supports API key authentication for secure access

Supported Operations:
    - Semantic Test Search: Vector-based search with advanced filtering
    - JIRA Key Lookup: Direct test retrieval by identifier
    - Similarity Analysis: Find tests similar to reference test
    - Data Ingestion: Trigger batch test data processing
    - Health Monitoring: Service status and collection statistics

Tool Capabilities:
    1. search_tests: Semantic search with filters (tags, priority, platforms, etc.)
    2. get_test_by_jira: Direct test lookup by JIRA key identifier
    3. find_similar_tests: Similarity search with configurable scope
    4. ingest_tests: Batch data ingestion from JSON files
    5. check_health: Service health and collection status monitoring

Dependencies:
    - mcp.server: Core MCP server framework and protocol implementation
    - httpx: Async HTTP client for API communication
    - structlog: Structured logging for debugging and monitoring
    - dotenv: Environment variable management

Used by:
    - Claude Desktop: AI assistant integration via MCP protocol
    - Development Tools: IDE extensions and automation scripts
    - AI Agents: Test discovery and analysis workflows
    - QA Automation: Test selection and validation pipelines

Complexity:
    - Tool registration: O(1) constant time schema definitions
    - Request handling: O(1) + network latency for HTTP operations
    - Response formatting: O(r) where r=number of results to format
    - Error handling: O(1) constant time exception processing

Performance Characteristics:
    - HTTP Client: 30-second timeout with connection pooling
    - Response Formatting: Efficient string building with pagination
    - Error Recovery: Graceful degradation with detailed error messages
    - Memory Usage: O(r) where r=result set size for formatting"""

import asyncio
import os
from collections.abc import Sequence
from typing import Any, Optional

import httpx
import structlog
from dotenv import load_dotenv

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = structlog.get_logger()

# Get API configuration from environment
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY") or os.environ.get("MASTER_API_KEY")

# Create the MCP server
server = Server("mlb-qbench")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Register and return the complete list of available MCP tools.
    
    This function defines the tool registry for the MCP server, providing
    JSON schema definitions for each tool's input parameters and capabilities.
    The schemas enable automatic validation and type checking by MCP clients.
    
    Returns:
        List of Tool objects with complete schema definitions for:
        - search_tests: Semantic search with advanced filtering
        - get_test_by_jira: Direct test lookup by JIRA identifier
        - find_similar_tests: Similarity analysis with scope control
        - ingest_tests: Batch data ingestion capabilities
        - check_health: Service monitoring and status reporting
        
    Tool Schema Features:
        - Type validation for all parameters
        - Enum constraints for priority and scope values
        - Array specifications for tags, platforms, and folder structures
        - Default values for optional parameters (top_k=20, scope="all")
        - Required parameter enforcement
        
    Complexity: O(1) - Static tool definitions with constant registration time
    
    MCP Protocol:
        This function is called once during server initialization to register
        available tools with the client. The returned schemas are used for
        parameter validation and IDE autocompletion.
    """
    return [
        types.Tool(
            name="search_tests",
            description="Search for tests using semantic search with optional filters",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query text",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 20)",
                        "default": 20,
                    },
                    "filters": {
                        "type": "object",
                        "description": "Optional filters to apply",
                        "properties": {
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags",
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["Critical", "High", "Medium", "Low"],
                                "description": "Filter by priority",
                            },
                            "platforms": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by platforms",
                            },
                            "folderStructure": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by folder structure",
                            },
                            "testType": {
                                "type": "string",
                                "description": "Filter by test type",
                            },
                            "relatedIssues": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by related issues",
                            },
                            "testPath": {
                                "type": "string",
                                "description": "Filter by test path pattern",
                            },
                        },
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_test_by_jira",
            description="Get a test by its JIRA key",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_key": {
                        "type": "string",
                        "description": "JIRA key to lookup (e.g., FRAMED-1390)",
                    }
                },
                "required": ["jira_key"],
            },
        ),
        types.Tool(
            name="find_similar_tests",
            description="Find tests similar to a given test",
            inputSchema={
                "type": "object",
                "properties": {
                    "jira_key": {
                        "type": "string",
                        "description": "JIRA key of the reference test",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of similar tests to return (default: 10)",
                        "default": 10,
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["docs", "steps", "all"],
                        "description": "Search scope (default: all)",
                        "default": "all",
                    },
                },
                "required": ["jira_key"],
            },
        ),
        types.Tool(
            name="ingest_tests",
            description="Trigger ingestion of test data from JSON files",
            inputSchema={
                "type": "object",
                "properties": {
                    "functional_path": {
                        "type": "string",
                        "description": "Path to functional tests JSON file",
                    },
                    "api_path": {
                        "type": "string",
                        "description": "Path to API tests JSON file",
                    },
                },
                "required": [],
            },
        ),
        types.Tool(
            name="check_health",
            description="Check the health status of the QBench service",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[dict[str, Any]] = None
) -> Sequence[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Execute MCP tool requests with comprehensive error handling and response formatting.
    
    This is the main orchestration function for all tool execution. It handles HTTP
    communication with the QBench API service, processes responses, and formats
    results for optimal AI assistant consumption.
    
    Args:
        name: Tool name to execute (search_tests, get_test_by_jira, etc.)
        arguments: Tool-specific parameters validated against registered schemas
        
    Returns:
        Sequence of MCP content objects (primarily TextContent with markdown formatting)
        
    Request Processing Pipeline:
        1. Authentication Setup: Configure API key headers if available
        2. HTTP Client Creation: Async client with 30-second timeout
        3. Tool Routing: Delegate to appropriate API endpoint
        4. Response Validation: HTTP status checking and JSON parsing
        5. Format Conversion: Transform API data to human-readable markdown
        6. Error Handling: Comprehensive exception management with context
        
    Tool Implementations:
        - search_tests: POST /search with query and filters
        - get_test_by_jira: GET /by-jira/{key} for direct lookup
        - find_similar_tests: GET /similar/{key} with similarity parameters
        - ingest_tests: POST /ingest for batch data processing
        - check_health: GET /healthz for service status monitoring
        
    Response Formatting Strategy:
        - Markdown formatting for rich text display in AI assistants
        - Truncation for long content (steps, descriptions)
        - Score display with 3 decimal precision for relevance
        - Hierarchical structure with headers and bullet points
        - Pagination indicators for truncated results
        
    Error Handling Categories:
        1. HTTP Status Errors: API endpoint failures with status codes
        2. JSON Parse Errors: Malformed response data handling
        3. Network Errors: Connection failures and timeouts
        4. Tool Errors: Unknown tool names and invalid parameters
        
    Complexity: O(1 + r) where r=number of results to format
    
    Performance Considerations:
        - HTTP connection pooling via httpx.AsyncClient context manager
        - 30-second timeout prevents hanging requests
        - Memory-efficient string building for large result sets
        - Lazy evaluation of response formatting
    """
    try:
        # Authentication setup: Prepare headers with API key if configured
        # Uses X-API-Key header for secure API access to QBench service
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["X-API-Key"] = API_KEY  # Add authentication header for protected endpoints

        # Create async HTTP client with connection pooling and timeout protection
        # 30-second timeout prevents hanging requests while allowing for complex queries
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            if name == "search_tests":
                # Semantic search execution: POST to /search endpoint with query and filters
                # Combines vector similarity search with metadata filtering for precise results
                response = await client.post(
                    f"{API_BASE_URL}/search",
                    json={
                        "query": arguments["query"],           # User search query for semantic matching
                        "top_k": arguments.get("top_k", 20),  # Result count limit (default: 20)
                        "filters": arguments.get("filters", {}),  # Optional metadata filters
                    },
                )
                response.raise_for_status()
                results = response.json()

                # Response formatting: Convert API results to markdown for AI assistant consumption
                # Returns user-friendly message if no results found
                if not results:
                    return [types.TextContent(type="text", text="No tests found matching your query.")]

                # Format each search result with hierarchical markdown structure
                formatted_results = []
                for i, result in enumerate(results, 1):
                    test = result["test"]
                    # Create numbered list with bold titles for visual hierarchy
                    text = f"**{i}. {test['title']}**\n"
                    text += f"- UID: {test['uid']}\n"  # Unique identifier for reference
                    text += f"- Priority: {test['priority']}\n"  # Business priority level
                    text += f"- Tags: {', '.join(test.get('tags', []))}\n"  # Metadata tags
                    text += f"- Score: {result['score']:.3f}\n"  # Relevance score (3 decimal precision)

                    # Include step-level matches if available (granular search results)
                    if result.get("matched_steps"):
                        text += f"- Matched Steps: {result['matched_steps']}\n"

                    # Truncate long summaries to prevent overwhelming output (200 char limit)
                    if test.get("summary"):
                        text += f"- Summary: {test['summary'][:200]}...\n"

                    text += "\n"  # Spacing between results for readability
                    formatted_results.append(text)

                return [types.TextContent(type="text", text="".join(formatted_results))]

            elif name == "get_test_by_jira":
                # Direct test lookup: GET by JIRA key for immediate test retrieval
                # Provides complete test details without similarity scoring
                response = await client.get(
                    f"{API_BASE_URL}/by-jira/{arguments['jira_key']}"  # Direct endpoint with key in path
                )
                response.raise_for_status()
                test = response.json()

                # Detailed test formatting: Comprehensive test information display
                # Provides complete metadata and abbreviated step information
                text = f"**{test['title']}**\n\n"  # Main title with markdown bold formatting
                text += f"- UID: {test['uid']}\n"  # Unique identifier
                text += f"- JIRA Key: {test.get('jiraKey', 'N/A')}\n"  # JIRA reference (fallback for null)
                text += f"- Priority: {test['priority']}\n"  # Business priority
                text += f"- Tags: {', '.join(test.get('tags', []))}\n"  # Metadata tags
                text += f"- Platforms: {', '.join(test.get('platforms', []))}\n"  # Target platforms

                # Include full summary if available (no truncation for single test)
                if test.get("summary"):
                    text += f"\n**Summary:**\n{test['summary']}\n"

                # Step preview: Show first 3 steps to avoid overwhelming output
                if test.get("steps"):
                    text += f"\n**Steps ({len(test['steps'])}):**\n"
                    for step in test["steps"][:3]:  # Limit to first 3 steps
                        text += f"{step['index']}. {step['action']}\n"
                        # Include expected results if available
                        if step.get("expected"):
                            text += f"   Expected: {', '.join(step['expected'])}\n"
                    # Indicate truncation if more steps exist
                    if len(test['steps']) > 3:
                        text += f"... and {len(test['steps']) - 3} more steps\n"

                return [types.TextContent(type="text", text=text)]

            elif name == "find_similar_tests":
                # Similarity analysis: Find tests similar to reference test using vector similarity
                # Configurable scope allows document-level, step-level, or combined analysis
                response = await client.get(
                    f"{API_BASE_URL}/similar/{arguments['jira_key']}",  # Reference test identifier
                    params={
                        "top_k": arguments.get("top_k", 10),      # Result count limit
                        "scope": arguments.get("scope", "all"),   # Search scope: docs/steps/all
                    },
                )
                response.raise_for_status()
                results = response.json()

                # Similarity results formatting: Display tests ranked by similarity score
                # Compact format focuses on key identifying information and relevance
                if not results:
                    return [types.TextContent(type="text", text="No similar tests found.")]

                # Header indicates reference test for context
                text = f"**Tests similar to {arguments['jira_key']}:**\n\n"
                for i, result in enumerate(results, 1):
                    test = result["test"]
                    text += f"{i}. **{test['title']}**\n"  # Numbered list with bold titles
                    text += f"   - UID: {test['uid']}\n"  # Unique identifier for reference
                    text += f"   - Similarity Score: {result['score']:.3f}\n"  # Relevance (3 decimal precision)
                    text += f"   - Tags: {', '.join(test.get('tags', []))}\n\n"  # Context tags for understanding similarity

                return [types.TextContent(type="text", text=text)]

            elif name == "ingest_tests":
                # Data ingestion trigger: POST to /ingest endpoint for batch processing
                # Supports both functional and API test data files with flexible payload
                payload = {}  # Build payload dynamically based on provided arguments
                if arguments.get("functional_path"):
                    payload["functional_path"] = arguments["functional_path"]  # Functional test JSON file
                if arguments.get("api_path"):
                    payload["api_path"] = arguments["api_path"]  # API test JSON file

                # Execute batch ingestion with constructed payload
                response = await client.post(
                    f"{API_BASE_URL}/ingest",
                    json=payload,  # Send file paths for server-side processing
                )
                response.raise_for_status()
                result = response.json()

                # Ingestion summary formatting: Display results for both test types
                # Shows document and step counts for verification of successful processing
                text = "**Ingestion Complete**\n\n"
                if "functional" in result:
                    # Functional test ingestion statistics
                    text += f"- Functional Tests: {result['functional']['docs_ingested']} docs, {result['functional']['steps_ingested']} steps\n"
                if "api" in result:
                    # API test ingestion statistics
                    text += f"- API Tests: {result['api']['docs_ingested']} docs, {result['api']['steps_ingested']} steps\n"

                return [types.TextContent(type="text", text=text)]

            elif name == "check_health":
                # Health monitoring: GET /healthz for comprehensive service status
                # Provides Qdrant collection status, embedder configuration, and system health
                response = await client.get(f"{API_BASE_URL}/healthz")
                response.raise_for_status()
                health = response.json()

                # Health status formatting: Comprehensive service monitoring display
                # Shows overall status, collection statistics, and embedder configuration
                text = f"**Service Health: {health['status'].upper()}**\n\n"

                # Qdrant vector database status and collection point counts
                if "qdrant" in health and health["qdrant"]["status"] == "connected":
                    text += "**Qdrant Collections:**\n"
                    for coll_name, coll_info in health["qdrant"]["collections"].items():
                        # Verify collection info structure before accessing point count
                        if isinstance(coll_info, dict) and "points_count" in coll_info:
                            text += f"- {coll_name}: {coll_info['points_count']} points\n"

                # Embedding provider configuration for troubleshooting
                if "embedder" in health:
                    text += "\n**Embedder:**\n"
                    text += f"- Provider: {health['embedder']['provider']}\n"  # OpenAI, Cohere, etc.
                    text += f"- Model: {health['embedder']['model']}\n"  # Specific model name

                return [types.TextContent(type="text", text=text)]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    # Comprehensive error handling with detailed context for debugging
    except httpx.HTTPStatusError as e:
        # HTTP status errors: Extract detailed error information from API response
        error_detail = ""
        try:
            # Attempt to parse JSON error response for detailed API error messages
            error_detail = e.response.json().get("detail", "")
        except Exception:
            # Fallback to raw response text if JSON parsing fails
            error_detail = e.response.text
        return [
            types.TextContent(
                type="text",
                text=f"API Error ({e.response.status_code}): {error_detail or str(e)}",
            )
        ]
    except Exception as e:
        # General exception handling: Log for debugging and return user-friendly message
        logger.error("Tool execution error", tool=name, error=str(e))
        return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Initialize and run the MCP server with stdio transport.
    
    This function sets up the MCP server infrastructure and runs the main
    event loop for handling client connections via stdio transport. The server
    operates in a request-response mode, processing tool calls and returning
    formatted results.
    
    Server Configuration:
        - Name: "mlb-qbench" for client identification
        - Version: "0.1.0" for compatibility tracking
        - Transport: stdio for desktop application integration
        - Capabilities: Standard MCP tool execution and notification support
        
    Initialization Process:
        1. Create InitializationOptions with server metadata
        2. Configure server capabilities and experimental features
        3. Establish stdio communication streams
        4. Run main server event loop with exception handling
        
    Complexity: O(∞) - Long-running server process
    
    Exception Handling:
        - raise_exceptions=False prevents server crashes on tool errors
        - Errors are logged and returned as error responses to clients
        - Server continues running after individual tool failures
        
    Transport Protocol:
        Uses stdio (stdin/stdout) for communication with MCP clients
        like Claude Desktop, enabling seamless AI assistant integration.
    """
    # Server configuration: Set up MCP server metadata and capabilities
    # Provides client identification and feature compatibility information
    init_options = InitializationOptions(
        server_name="mlb-qbench",      # Unique server identifier for client recognition
        server_version="0.1.0",        # Version for compatibility and debugging
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),  # Standard notification support
            experimental_capabilities={},                # No experimental features enabled
        ),
    )

    # Main server execution: Run MCP server with stdio transport
    # Uses async context manager for proper resource cleanup
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,          # stdin for receiving client requests
            write_stream,         # stdout for sending responses
            init_options,         # Server configuration and capabilities
            raise_exceptions=False,  # Graceful error handling (don't crash server)
        )


# Main execution: Start MCP server when run as script
if __name__ == "__main__":
    # Run async main function in new event loop
    # This allows the server to handle concurrent tool requests
    asyncio.run(main())
