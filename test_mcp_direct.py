#!/usr/bin/env python3
"""Test MCP imports directly."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")

# Try the imports that fail in server.py
try:
    import mcp.server.stdio
    import mcp.types as types
    from mcp.server import NotificationOptions, Server
    from mcp.server.models import InitializationOptions
    print("✓ All MCP imports successful!")
except ImportError as e:
    print(f"✗ ImportError: {e}")
    
# Now try importing the server module
try:
    from src.mcp.server import main
    print("✓ Successfully imported src.mcp.server.main")
except ImportError as e:
    print(f"✗ ImportError importing server: {e}")