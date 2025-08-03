#!/usr/bin/env python3
"""Wrapper script for MCP server to handle working directory issues.

This module serves as an entry point wrapper for the MCP (Model Context Protocol) server,
ensuring proper working directory setup and Python path configuration before launching
the main server application.

The wrapper performs the following operations:
1. Sets the working directory to the script's location
2. Adds the project root to Python's module search path
3. Imports and runs the MCP server's main async function

This approach resolves potential import and path issues that may occur when running
the MCP server from different locations or environments.

Dependencies:
    - src.mcp.server: The main MCP server module containing the server implementation
    - asyncio: Python's async/await framework for running the async server

Execution:
    Run directly as a script: python mcp_wrapper.py
"""

import os
import sys

# Ensure we're in the correct directory
# This guarantees that relative imports and file operations work correctly
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the project root to Python path
# This allows importing modules from src/ without installation
sys.path.insert(0, script_dir)

# Import and run the MCP server
from src.mcp.server import main
import asyncio

if __name__ == "__main__":
    # Launch the MCP server using asyncio's event loop
    # The main() function is expected to be an async coroutine
    asyncio.run(main())