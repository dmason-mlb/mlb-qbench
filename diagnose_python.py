#!/usr/bin/env python3
"""Diagnostic script to collect and export Python environment information.

This script gathers comprehensive diagnostic information about the Python
environment, system paths, and installed packages. It's designed to help
troubleshoot environment-related issues, particularly with Claude Desktop
integration and MCP package dependencies.

The diagnostic data includes:
- Python executable path and version
- System PATH environment variable
- Python module search paths (sys.path)
- Current working directory
- Location of python3 command
- Installed packages containing 'mcp'

The collected information is:
1. Printed to stdout in JSON format for immediate viewing
2. Written to /tmp/mlb_qbench_diagnostics.json for external tools

This dual output approach ensures the diagnostics are accessible both
in terminal sessions and to external tools like Claude Desktop.

Dependencies:
    - subprocess: For running system commands
    - json: For structured data export

Usage:
    python diagnose_python.py

Output:
    - JSON formatted diagnostic data to stdout
    - Diagnostic file at /tmp/mlb_qbench_diagnostics.json
"""

import sys
import os
import subprocess
import json

# Initialize diagnostic data structure with all environment information
diagnostics = {
    "python_executable": sys.executable,
    "python_version": sys.version,
    "sys_path": sys.path,
    "cwd": os.getcwd(),
    "env_PATH": os.environ.get("PATH", "").split(":"),
    "which_python3": None,
    "pip_list_mcp": []
}

# Determine the system location of python3 command
# This helps identify if there's a mismatch between system Python and current Python
try:
    result = subprocess.run(["which", "python3"], capture_output=True, text=True)
    diagnostics["which_python3"] = result.stdout.strip()
except:
    # Silently handle errors (e.g., 'which' not available on Windows)
    pass

# Search for any pip packages containing 'mcp' in their name
# This helps verify if the MCP package is installed and under what name
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'mcp' in line.lower():
            diagnostics["pip_list_mcp"].append(line.strip())
except:
    # Silently handle pip errors (e.g., pip not installed)
    pass

# Write diagnostics to a temporary file for external tool access
# Claude Desktop and other tools can read this file to understand the environment
with open("/tmp/mlb_qbench_diagnostics.json", "w") as f:
    json.dump(diagnostics, f, indent=2)

# Also output to stdout for immediate visibility
print(json.dumps(diagnostics, indent=2))