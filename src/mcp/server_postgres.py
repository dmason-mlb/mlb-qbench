"""Model Context Protocol (MCP) server for MLB QBench with PostgreSQL backend.

This module implements the MCP server using PostgreSQL + pgvector instead of Qdrant,
providing the same test search and management capabilities through the MCP interface.
"""

import asyncio
import os
from collections.abc import Sequence
from typing import Any, Optional

import structlog
from dotenv import load_dotenv

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from ..db.postgres_vector import PostgresVectorDB
from ..embedder import get_embedder, prepare_text_for_embedding
from ..models.test_models import TestDoc

# Load environment variables
load_dotenv()

# Configure logging
logger = structlog.get_logger()

# Create the MCP server
server = Server("mlb-qbench-postgres")

# Global instances
db: Optional[PostgresVectorDB] = None
embedder = None


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Register available MCP tools for PostgreSQL-backed QBench."""
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
                    "uid": {
                        "type": "string",
                        "description": "UID of the reference test",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of similar tests to return (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["uid"],
            },
        ),
        types.Tool(
            name="check_health",
            description="Check the health status of the PostgreSQL QBench service",
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
    """Execute MCP tool requests using PostgreSQL backend."""
    global db, embedder
    
    try:
        # Initialize database and embedder if needed
        if db is None:
            db = PostgresVectorDB()
            await db.initialize()
            logger.info("PostgreSQL connection initialized for MCP")
            
        if embedder is None:
            embedder = get_embedder()
            logger.info("Embedder initialized for MCP")
        
        if name == "search_tests":
            # Prepare and embed query
            query = arguments["query"]
            prepared_query = prepare_text_for_embedding(query)
            query_embedding = await embedder.embed(prepared_query)
            
            # Build filters
            filters = {}
            if arguments.get("filters"):
                input_filters = arguments["filters"]
                if input_filters.get("priority"):
                    filters["priority"] = input_filters["priority"]
                if input_filters.get("tags"):
                    filters["tags"] = input_filters["tags"]
                if input_filters.get("platforms"):
                    filters["platforms"] = input_filters["platforms"]
                if input_filters.get("folderStructure"):
                    filters["folderStructure"] = input_filters["folderStructure"]
                if input_filters.get("testType"):
                    filters["testType"] = input_filters["testType"]
            
            # Perform search
            results = await db.hybrid_search(
                query_embedding=query_embedding,
                filters=filters,
                limit=arguments.get("top_k", 20),
                include_steps=True
            )
            
            if not results:
                return [types.TextContent(type="text", text="No tests found matching your query.")]
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                text = f"**{i}. {result['title']}**\n"
                text += f"- UID: {result['uid']}\n"
                text += f"- JIRA Key: {result.get('jira_key', 'N/A')}\n"
                text += f"- Priority: {result.get('priority', 'N/A')}\n"
                text += f"- Tags: {', '.join(result.get('tags', []))}\n"
                text += f"- Similarity: {result['similarity']:.3f}\n"
                
                if result.get("matched_steps"):
                    text += f"- Matched Steps: {len(result['matched_steps'])} steps\n"
                
                if result.get("summary"):
                    text += f"- Summary: {result['summary'][:200]}...\n"
                
                text += "\n"
                formatted_results.append(text)
            
            return [types.TextContent(type="text", text="".join(formatted_results))]
        
        elif name == "get_test_by_jira":
            # Lookup by JIRA key
            test = await db.search_by_jira_key(arguments["jira_key"])
            
            if not test:
                return [types.TextContent(
                    type="text",
                    text=f"No test found with JIRA key: {arguments['jira_key']}"
                )]
            
            # Format test details
            text = f"**{test['title']}**\n\n"
            text += f"- UID: {test['uid']}\n"
            text += f"- JIRA Key: {test.get('jira_key', 'N/A')}\n"
            text += f"- Priority: {test.get('priority', 'N/A')}\n"
            text += f"- Tags: {', '.join(test.get('tags', []))}\n"
            text += f"- Platforms: {', '.join(test.get('platforms', []))}\n"
            text += f"- Test Type: {test.get('test_type', 'N/A')}\n"
            
            if test.get("summary"):
                text += f"\n**Summary:**\n{test['summary']}\n"
            
            if test.get("description"):
                text += f"\n**Description:**\n{test['description'][:500]}...\n"
            
            if test.get("steps"):
                text += f"\n**Steps ({len(test['steps'])}):**\n"
                for step in test["steps"][:3]:
                    text += f"{step['index']}. {step['action']}\n"
                    if step.get("expected"):
                        text += f"   Expected: {', '.join(step['expected'])}\n"
                if len(test["steps"]) > 3:
                    text += f"... and {len(test['steps']) - 3} more steps\n"
            
            return [types.TextContent(type="text", text=text)]
        
        elif name == "find_similar_tests":
            # Find similar tests
            similar_tests = await db.find_similar_tests(
                test_uid=arguments["uid"],
                limit=arguments.get("top_k", 10)
            )
            
            if not similar_tests:
                return [types.TextContent(type="text", text="No similar tests found.")]
            
            # Format results
            text = f"**Tests similar to {arguments['uid']}:**\n\n"
            for i, test in enumerate(similar_tests, 1):
                text += f"{i}. **{test['title']}**\n"
                text += f"   - UID: {test['uid']}\n"
                text += f"   - JIRA Key: {test.get('jira_key', 'N/A')}\n"
                text += f"   - Similarity: {test['similarity']:.3f}\n"
                text += f"   - Tags: {', '.join(test.get('tags', []))}\n\n"
            
            return [types.TextContent(type="text", text=text)]
        
        elif name == "check_health":
            # Get database statistics
            stats = await db.get_statistics()
            
            # Format health status
            text = "**Service Health: HEALTHY**\n\n"
            text += "**PostgreSQL Database:**\n"
            text += f"- Status: Connected\n"
            text += f"- Total Documents: {stats.get('total_documents', 0)}\n"
            text += f"- Total Steps: {stats.get('total_steps', 0)}\n"
            
            if stats.get("priority_distribution"):
                text += "\n**Priority Distribution:**\n"
                for priority, count in stats["priority_distribution"].items():
                    text += f"- {priority}: {count} tests\n"
            
            if stats.get("test_type_distribution"):
                text += "\n**Test Type Distribution:**\n"
                for test_type, count in stats["test_type_distribution"].items():
                    text += f"- {test_type}: {count} tests\n"
            
            text += "\n**Embedder:**\n"
            text += f"- Provider: {os.getenv('EMBED_PROVIDER', 'openai')}\n"
            text += f"- Model: {os.getenv('EMBED_MODEL', 'text-embedding-3-large')}\n"
            
            return [types.TextContent(type="text", text=text)]
        
        else:
            return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        logger.error("Tool execution error", tool=name, error=str(e))
        return [types.TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    """Initialize and run the PostgreSQL-backed MCP server."""
    global db, embedder
    
    # Initialize database and embedder at startup
    try:
        db = PostgresVectorDB()
        await db.initialize()
        logger.info("PostgreSQL initialized for MCP server")
        
        embedder = get_embedder()
        logger.info("Embedder initialized for MCP server")
        
        # Get initial statistics
        stats = await db.get_statistics()
        logger.info("Database ready", 
                   total_documents=stats.get("total_documents", 0),
                   total_steps=stats.get("total_steps", 0))
    except Exception as e:
        logger.error("Failed to initialize MCP server", error=str(e))
        raise
    
    # Server configuration
    init_options = InitializationOptions(
        server_name="mlb-qbench-postgres",
        server_version="2.0.0",
        capabilities=server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
    
    # Run MCP server with stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            init_options,
            raise_exceptions=False,
        )


if __name__ == "__main__":
    asyncio.run(main())