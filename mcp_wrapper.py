#!/usr/bin/env python3
"""Wrapper script for MCP server to handle working directory issues."""

import os
import sys

# Ensure we're in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the project root to Python path
sys.path.insert(0, script_dir)

# Import and run the MCP server
from src.mcp.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())