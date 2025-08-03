#!/usr/bin/env python3
"""Enhanced wrapper with diagnostics."""

import os
import sys
import subprocess

# First, run diagnostics
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Log Python environment
with open("/tmp/claude_desktop_python.log", "w") as f:
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Working directory: {os.getcwd()}\n")
    f.write(f"Script directory: {script_dir}\n")
    f.write("\nPython path:\n")
    for p in sys.path:
        f.write(f"  - {p}\n")
    
    # Check if mcp is importable
    f.write("\nChecking mcp import:\n")
    try:
        import mcp
        f.write(f"✓ mcp found at: {mcp.__file__}\n")
    except ImportError as e:
        f.write(f"✗ mcp not found: {e}\n")
        
        # Try to install it
        f.write("\nAttempting to install mcp...\n")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "mcp"], 
                              capture_output=True, text=True)
        f.write(f"Install stdout: {result.stdout}\n")
        f.write(f"Install stderr: {result.stderr}\n")

# Add paths
sys.path.insert(0, script_dir)

# Now try to import and run
from src.mcp.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())