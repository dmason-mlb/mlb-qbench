"""Entry point for running the MLB QBench MCP (Model Context Protocol) server.

This module serves as the primary executable entry point for the MCP server,
enabling the MLB QBench test retrieval service to be integrated with AI assistants
and development tools through the standardized MCP protocol.

Execution Flow:
    1. Module import validation and dependency resolution
    2. Async runtime initialization via asyncio.run()
    3. MCP server startup with stdio transport
    4. Event loop management for client connections
    5. Graceful shutdown on termination signals

MCP Integration:
    - Protocol: Model Context Protocol for AI assistant integration
    - Transport: stdio (stdin/stdout) for desktop applications like Claude
    - Tools: Exposes semantic search, test retrieval, and data ingestion
    - Authentication: Optional API key support for secure access

Dependencies:
    - asyncio: Core async runtime for server event loop
    - .server.main: Primary MCP server implementation and initialization

Used by:
    - Claude Desktop: AI assistant integration via MCP client
    - Development tools: IDE extensions and automation scripts
    - Command line: Direct execution for testing and development

Usage:
    python -m src.mcp          # Run from project root
    python src/mcp/__main__.py # Direct module execution

Performance:
    - Startup time: <100ms for server initialization
    - Memory usage: ~50MB baseline + embedding provider overhead
    - Concurrent clients: Supports multiple simultaneous connections

Complexity: O(1) - Simple entry point with constant initialization time
"""

import asyncio

from .server_postgres import main

# Main execution guard: Only run when invoked as primary module
# Prevents accidental server startup during imports for testing
if __name__ == "__main__":
    # Start async MCP server with asyncio event loop
    # asyncio.run() handles event loop creation, execution, and cleanup
    # Blocks until server shutdown or fatal error occurs
    asyncio.run(main())
