#!/usr/bin/env python3
"""Enhanced MCP server wrapper with comprehensive diagnostics and auto-recovery.

This enhanced wrapper extends the basic mcp_wrapper.py with diagnostic logging
and automatic recovery mechanisms. It's designed to diagnose and resolve common
issues that prevent the MCP server from starting, particularly in Claude Desktop
environments.

Key features:
1. Comprehensive environment logging to /tmp/claude_desktop_python.log
2. Automatic detection of missing MCP package
3. Automatic installation attempt if MCP is not found
4. Detailed error logging for troubleshooting
5. Path configuration and server launch

The diagnostic log includes:
- Python executable and version information
- Working directory and script location
- Complete Python path (sys.path)
- MCP package availability and location
- Installation attempt results if needed

This wrapper is particularly useful when:
- Debugging Claude Desktop integration issues
- MCP package installation is uncertain
- Python environment configuration needs investigation
- Automatic recovery from missing dependencies is desired

Dependencies:
    - subprocess: For pip installation attempts
    - src.mcp.server: The main MCP server module
    - asyncio: For running the async server

Usage:
    python mcp_wrapper_diagnostic.py

Output:
    - Diagnostic log at /tmp/claude_desktop_python.log
    - MCP server starts if successful
    - Error messages to stderr if startup fails
"""

import os
import sys
import subprocess

# Establish script directory and change to it for consistent relative paths
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Create comprehensive diagnostic log for troubleshooting
# This log file helps debug issues in Claude Desktop or other environments
with open("/tmp/claude_desktop_python.log", "w") as f:
    # Log basic Python environment information
    f.write(f"Python executable: {sys.executable}\n")
    f.write(f"Python version: {sys.version}\n")
    f.write(f"Working directory: {os.getcwd()}\n")
    f.write(f"Script directory: {script_dir}\n")
    
    # Log all Python module search paths for import debugging
    f.write("\nPython path:\n")
    for p in sys.path:
        f.write(f"  - {p}\n")
    
    # Check if the MCP package is available in the current environment
    f.write("\nChecking mcp import:\n")
    try:
        import mcp
        f.write(f"✓ mcp found at: {mcp.__file__}\n")
    except ImportError as e:
        f.write(f"✗ mcp not found: {e}\n")
        
        # Attempt automatic recovery by installing the missing package
        # This helps in environments where the package wasn't pre-installed
        f.write("\nAttempting to install mcp...\n")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "mcp"], 
                              capture_output=True, text=True)
        f.write(f"Install stdout: {result.stdout}\n")
        f.write(f"Install stderr: {result.stderr}\n")

# Configure Python path to include project root
# This enables importing from src/ without package installation
sys.path.insert(0, script_dir)

# Import and prepare to run the MCP server
from src.mcp.server import main
import asyncio

if __name__ == "__main__":
    # Launch the MCP server using asyncio event loop
    asyncio.run(main())