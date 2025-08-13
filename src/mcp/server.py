"""MCP server implementation for MLB QBench."""

import asyncio
import os
from collections.abc import Sequence
from typing import Any, Optional

import httpx
import structlog

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Configure logging
logger = structlog.get_logger()

# Get API configuration from environment
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
API_KEY = os.environ.get("API_KEY")

# Create the MCP server
server = Server("mlb-qbench")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Return list of available tools."""
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
    """Handle tool execution."""
    try:
        # Prepare headers with API key if configured
        headers = {"Content-Type": "application/json"}
        if API_KEY:
            headers["X-API-Key"] = API_KEY

        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            if name == "search_tests":
                # Execute search
                response = await client.post(
                    f"{API_BASE_URL}/search",
                    json={
                        "query": arguments["query"],
                        "top_k": arguments.get("top_k", 20),
                        "filters": arguments.get("filters", {}),
                    },
                )
                response.raise_for_status()
                results = response.json()

                # Format results
                if not results:
                    return [types.TextContent(type="text", text="No tests found matching your query.")]

                formatted_results = []
                for i, result in enumerate(results, 1):
                    test = result["test"]
                    text = f"**{i}. {test['title']}**\n"
                    text += f"- UID: {test['uid']}\n"
                    text += f"- Priority: {test['priority']}\n"
                    text += f"- Tags: {', '.join(test.get('tags', []))}\n"
                    text += f"- Score: {result['score']:.3f}\n"

                    if result.get("matched_steps"):
                        text += f"- Matched Steps: {result['matched_steps']}\n"

                    if test.get("summary"):
                        text += f"- Summary: {test['summary'][:200]}...\n"

                    text += "\n"
                    formatted_results.append(text)

                return [types.TextContent(type="text", text="".join(formatted_results))]

            elif name == "get_test_by_jira":
                # Get test by JIRA key
                response = await client.get(
                    f"{API_BASE_URL}/by-jira/{arguments['jira_key']}"
                )
                response.raise_for_status()
                test = response.json()

                # Format test details
                text = f"**{test['title']}**\n\n"
                text += f"- UID: {test['uid']}\n"
                text += f"- JIRA Key: {test.get('jiraKey', 'N/A')}\n"
                text += f"- Priority: {test['priority']}\n"
                text += f"- Tags: {', '.join(test.get('tags', []))}\n"
                text += f"- Platforms: {', '.join(test.get('platforms', []))}\n"

                if test.get("summary"):
                    text += f"\n**Summary:**\n{test['summary']}\n"

                if test.get("steps"):
                    text += f"\n**Steps ({len(test['steps'])}):**\n"
                    for step in test["steps"][:3]:  # Show first 3 steps
                        text += f"{step['index']}. {step['action']}\n"
                        if step.get("expected"):
                            text += f"   Expected: {', '.join(step['expected'])}\n"
                    if len(test['steps']) > 3:
                        text += f"... and {len(test['steps']) - 3} more steps\n"

                return [types.TextContent(type="text", text=text)]

            elif name == "find_similar_tests":
                # Find similar tests
                response = await client.get(
                    f"{API_BASE_URL}/similar/{arguments['jira_key']}",
                    params={
                        "top_k": arguments.get("top_k", 10),
                        "scope": arguments.get("scope", "all"),
                    },
                )
                response.raise_for_status()
                results = response.json()

                # Format results
                if not results:
                    return [types.TextContent(type="text", text="No similar tests found.")]

                text = f"**Tests similar to {arguments['jira_key']}:**\n\n"
                for i, result in enumerate(results, 1):
                    test = result["test"]
                    text += f"{i}. **{test['title']}**\n"
                    text += f"   - UID: {test['uid']}\n"
                    text += f"   - Similarity Score: {result['score']:.3f}\n"
                    text += f"   - Tags: {', '.join(test.get('tags', []))}\n\n"

                return [types.TextContent(type="text", text=text)]

            elif name == "ingest_tests":
                # Trigger ingestion
                payload = {}
                if arguments.get("functional_path"):
                    payload["functional_path"] = arguments["functional_path"]
                if arguments.get("api_path"):
                    payload["api_path"] = arguments["api_path"]

                response = await client.post(
                    f"{API_BASE_URL}/ingest",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                text = "**Ingestion Complete**\n\n"
                if "functional" in result:
                    text += f"- Functional Tests: {result['functional']['docs_ingested']} docs, {result['functional']['steps_ingested']} steps\n"
                if "api" in result:
                    text += f"- API Tests: {result['api']['docs_ingested']} docs, {result['api']['steps_ingested']} steps\n"

                return [types.TextContent(type="text", text=text)]

            elif name == "check_health":
                # Check health
                response = await client.get(f"{API_BASE_URL}/healthz")
                response.raise_for_status()
                health = response.json()

                text = f"**Service Health: {health['status'].upper()}**\n\n"

                if "qdrant" in health and health["qdrant"]["status"] == "connected":
                    text += "**Qdrant Collections:**\n"
                    for coll_name, coll_info in health["qdrant"]["collections"].items():
                        if isinstance(coll_info, dict) and "points_count" in coll_info:
                            text += f"- {coll_name}: {coll_info['points_count']} points\n"

                if "embedder" in health:
                    text += "\n**Embedder:**\n"
                    text += f"- Provider: {health['embedder']['provider']}\n"
                    text += f"- Model: {health['embedder']['model']}\n"

                return [types.TextContent(type="text", text=text)]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.json().get("detail", "")
        except Exception:
            error_detail = e.response.text
        return [
            types.TextContent(
                type="text",
                text=f"API Error ({e.response.status_code}): {error_detail or str(e)}",
            )
        ]
    except Exception as e:
        logger.error("Tool execution error", tool=name, error=str(e))
        return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Run the MCP server."""
    # Configure the server
    init_options = InitializationOptions(
        server_name="mlb-qbench",
        server_version="0.1.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )

    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            init_options,
            raise_exceptions=False,
        )


if __name__ == "__main__":
    asyncio.run(main())
