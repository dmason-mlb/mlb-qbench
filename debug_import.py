#!/usr/bin/env python3
"""Debug script to diagnose Python import issues with the MCP package.

This diagnostic tool helps troubleshoot import problems related to the Model Context
Protocol (MCP) package and the project's module structure. It provides detailed
information about the Python environment, installed packages, and import paths.

The script performs the following diagnostic steps:
1. Displays Python version and environment information
2. Shows all paths in sys.path for module resolution debugging
3. Attempts to import the 'mcp' package and reports its location
4. Checks pip for installed packages containing 'mcp'
5. Tests different import strategies for the local src.mcp module
6. Provides guidance on resolving common import issues

This is particularly useful when debugging:
- Module not found errors
- Import path configuration issues
- Package installation problems
- Virtual environment setup issues

Dependencies:
    - subprocess: For running pip commands to check installed packages
    - No external packages required (diagnostic only)

Usage:
    python debug_import.py

Output:
    Prints diagnostic information to stdout with success/failure indicators
"""

import os
import sys
import subprocess

# Display basic Python environment information
print("=== Python Import Debug ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")

# Display all module search paths to help diagnose import resolution
print(f"\nPython path:")
for i, path in enumerate(sys.path):
    print(f"  [{i}] {path}")

# Test if the 'mcp' package is importable and show its location
print("\n=== Checking for 'mcp' package ===")
try:
    import mcp
    print(f"✓ 'mcp' module found at: {mcp.__file__}")
except ImportError as e:
    print(f"✗ ImportError: {e}")

# Check installed packages for any containing 'mcp' in the name
# This helps identify if the package is installed with a different name
print("\n=== Checking pip list for 'mcp' ===")
result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                       capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'mcp' in line.lower():
        print(f"  {line}")

print("\n=== Attempting different import strategies ===")

# Try importing from src by adding project root to path
# This tests if the local src.mcp module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print(f"Added to path: {os.path.dirname(os.path.abspath(__file__))}")

try:
    from src.mcp import server
    print("✓ Successfully imported: from src.mcp import server")
except ImportError as e:
    print(f"✗ ImportError: {e}")

# Provide guidance on resolving the import issue
print("\n=== Checking if we need to install mcp package ===")
print("The 'mcp' imports in server.py suggest it needs the Model Context Protocol package")
print("Run: pip install mcp")