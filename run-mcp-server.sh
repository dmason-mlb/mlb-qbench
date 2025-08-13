#!/bin/bash

# Change to the project directory
cd "$(dirname "$0")"

# Run the MCP server
exec .venv/bin/python -m src.mcp.server "$@"