#!/usr/bin/env python3
"""Diagnostic script to identify Python environment issues."""

import sys
import os
import subprocess
import json

# Create diagnostic info
diagnostics = {
    "python_executable": sys.executable,
    "python_version": sys.version,
    "sys_path": sys.path,
    "cwd": os.getcwd(),
    "env_PATH": os.environ.get("PATH", "").split(":"),
    "which_python3": None,
    "pip_list_mcp": []
}

# Get which python3
try:
    result = subprocess.run(["which", "python3"], capture_output=True, text=True)
    diagnostics["which_python3"] = result.stdout.strip()
except:
    pass

# Check for mcp in pip
try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if 'mcp' in line.lower():
            diagnostics["pip_list_mcp"].append(line.strip())
except:
    pass

# Write to file for Claude Desktop to see
with open("/tmp/mlb_qbench_diagnostics.json", "w") as f:
    json.dump(diagnostics, f, indent=2)

print(json.dumps(diagnostics, indent=2))