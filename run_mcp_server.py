#!/usr/bin/env python
"""Direct runner for MCP server that handles imports properly."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure structlog to use stderr for ALL modules
# This must be done before importing any modules that use structlog
import structlog
structlog.configure(
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)

from src.mcp.server_postgres import main

if __name__ == "__main__":
    asyncio.run(main())
