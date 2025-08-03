#!/usr/bin/env python3
"""Test MCP imports directly to verify package installation and module structure.

This test script specifically validates the Model Context Protocol (MCP) package
imports that are required by the server.py module. It tests both the external
MCP package dependencies and the local src.mcp.server module import.

The script performs two main import tests:
1. External MCP package imports - Tests all MCP components used by the server
2. Local module import - Tests the project's src.mcp.server module

This is useful for:
- Verifying MCP package is correctly installed
- Ensuring all required MCP submodules are available
- Testing that the local project structure allows proper imports
- Debugging import errors before running the full server

Dependencies:
    - mcp: Model Context Protocol package (external dependency)
    - src.mcp.server: Local server module

Usage:
    python test_mcp_direct.py

Expected output:
    - Python environment information
    - Success/failure status for each import test
    - Specific error messages if imports fail
"""

import sys
import os

# Add project root to path to enable local imports
# This ensures src.mcp.server can be imported without installation
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Display Python environment for debugging
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Test all MCP package imports required by server.py
# These imports will fail if the MCP package is not installed
try:
    import mcp.server.stdio
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    print("✓ All MCP imports successful!")
except ImportError as e:
    print(f"✗ ImportError: {e}")
    
# Test importing the local server module
# This validates that the project structure and path setup are correct
try:
    from src.mcp.server import main
    print("✓ Successfully imported src.mcp.server.main")
except ImportError as e:
    print(f"✗ ImportError importing server: {e}")