#!/usr/bin/env python3
"""Test module resolution behavior in virtual environment across different contexts.

This comprehensive test script validates how Python module resolution works
when using a virtual environment from different working directories. It tests
various scenarios to understand module import behavior, which is crucial for
tools like Claude Desktop that may invoke Python from unexpected locations.

The script tests three key scenarios:
1. Module imports from different working directories
2. Module imports with PYTHONPATH environment variable
3. Python -m flag behavior from different locations

Test coverage includes:
- Import behavior from project root, home directory, and system root
- sys.path[0] values in different contexts
- PYTHONPATH environment variable effects
- Python -m module execution from various directories

This helps diagnose issues where:
- Claude Desktop runs Python from unexpected directories
- Module imports fail due to working directory assumptions
- Virtual environment isolation is incomplete
- Path resolution differs between development and production

The script uses hardcoded paths specific to the development environment
to ensure consistent testing regardless of where it's executed from.

Dependencies:
    - subprocess: For running Python in controlled environments
    - No external packages required

Usage:
    python test_venv_module.py

Output:
    - Test results for each scenario with success/failure indicators
    - Detailed error messages when imports fail
    - Path information for debugging module resolution
"""

import os
import sys
import subprocess

print("=== Virtual Environment Module Test ===")
print(f"Python: {sys.executable}")
print(f"CWD: {os.getcwd()}")

# Define test directories to simulate different execution contexts
# These represent common scenarios where Python might be invoked
test_dirs = [
    "/Users/douglas.mason/Documents/GitHub/mlb-qbench",  # Project root
    "/Users/douglas.mason",                              # User home
    "/"                                                  # System root
]

# Test 1: Module import behavior from different working directories
for test_dir in test_dirs:
    print(f"\n--- Testing from directory: {test_dir} ---")
    
    # Construct command to test module import and display path information
    # This helps understand how Python resolves modules in different contexts
    cmd = [
        "/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python",
        "-c",
        "import os; import sys; print(f'CWD: {os.getcwd()}'); print(f'sys.path[0]: {sys.path[0]}'); import src.mcp; print('✓ src.mcp imported successfully')"
    ]
    
    # Execute Python in the specific working directory
    result = subprocess.run(
        cmd,
        cwd=test_dir,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print(f"✗ Failed: {result.stderr}")

# Test 2: Module import with PYTHONPATH environment variable
# This tests if PYTHONPATH can solve import issues from any directory
print("\n--- Testing with PYTHONPATH set ---")
env = os.environ.copy()
env["PYTHONPATH"] = "/Users/douglas.mason/Documents/GitHub/mlb-qbench"

cmd = [
    "/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python",
    "-c",
    "import os; import sys; print(f'PYTHONPATH: {os.environ.get(\"PYTHONPATH\")}'); import src.mcp; print('✓ src.mcp imported successfully')"
]

# Run from root directory to test PYTHONPATH effectiveness
result = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd="/")
if result.returncode == 0:
    print(result.stdout)
else:
    print(f"✗ Failed: {result.stderr}")

# Test 3: Python -m flag behavior for running modules as scripts
# The -m flag affects how Python sets up sys.path
print("\n--- Testing python -m src.mcp ---")
cmd = [
    "/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python",
    "-m", "src.mcp"
]

# Test from project root (should work)
result = subprocess.run(
    cmd,
    cwd="/Users/douglas.mason/Documents/GitHub/mlb-qbench",
    capture_output=True,
    text=True
)
print(f"From project root: {'✓ Success' if result.returncode == 0 else '✗ Failed'}")
if result.stderr:
    print(f"  Error: {result.stderr}")

# Test from home directory (likely to fail without PYTHONPATH)
result = subprocess.run(
    cmd,
    cwd="/Users/douglas.mason",
    capture_output=True,
    text=True
)
print(f"From home directory: {'✓ Success' if result.returncode == 0 else '✗ Failed'}")
if result.stderr:
    print(f"  Error: {result.stderr}")