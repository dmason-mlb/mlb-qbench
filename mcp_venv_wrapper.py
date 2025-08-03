#!/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python
"""MCP wrapper that ensures correct environment setup for venv."""

import os
import sys
import asyncio

# Set up the environment
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir  # This script is in the project root

# Change to project directory
os.chdir(project_root)

# Add project root to Python path
sys.path.insert(0, project_root)

# Verify we can import
try:
    from src.mcp.server import main
except ImportError as e:
    # Log error to stderr for Claude Desktop
    print(f"Import error: {e}", file=sys.stderr)
    print(f"Working directory: {os.getcwd()}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    sys.exit(1)

# Run the server
if __name__ == "__main__":
    asyncio.run(main())