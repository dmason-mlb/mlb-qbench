#!/usr/bin/env python3
"""Debug script to understand the import issue."""

import os
import sys
import subprocess

print("=== Python Import Debug ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"\nPython path:")
for i, path in enumerate(sys.path):
    print(f"  [{i}] {path}")

print("\n=== Checking for 'mcp' package ===")
try:
    import mcp
    print(f"✓ 'mcp' module found at: {mcp.__file__}")
except ImportError as e:
    print(f"✗ ImportError: {e}")

print("\n=== Checking pip list for 'mcp' ===")
result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                       capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'mcp' in line.lower():
        print(f"  {line}")

print("\n=== Attempting different import strategies ===")

# Try importing from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print(f"Added to path: {os.path.dirname(os.path.abspath(__file__))}")

try:
    from src.mcp import server
    print("✓ Successfully imported: from src.mcp import server")
except ImportError as e:
    print(f"✗ ImportError: {e}")

# Check if mcp-python is what we need
print("\n=== Checking if we need to install mcp package ===")
print("The 'mcp' imports in server.py suggest it needs the Model Context Protocol package")
print("Run: pip install mcp")