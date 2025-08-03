#!/usr/bin/env python3
"""Test module resolution in venv."""

import os
import sys
import subprocess

print("=== Virtual Environment Module Test ===")
print(f"Python: {sys.executable}")
print(f"CWD: {os.getcwd()}")

# Test different working directories
test_dirs = [
    "/Users/douglas.mason/Documents/GitHub/mlb-qbench",
    "/Users/douglas.mason",
    "/"
]

for test_dir in test_dirs:
    print(f"\n--- Testing from directory: {test_dir} ---")
    
    # Test module import
    cmd = [
        "/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python",
        "-c",
        "import os; import sys; print(f'CWD: {os.getcwd()}'); print(f'sys.path[0]: {sys.path[0]}'); import src.mcp; print('✓ src.mcp imported successfully')"
    ]
    
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

# Test with PYTHONPATH
print("\n--- Testing with PYTHONPATH set ---")
env = os.environ.copy()
env["PYTHONPATH"] = "/Users/douglas.mason/Documents/GitHub/mlb-qbench"

cmd = [
    "/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python",
    "-c",
    "import os; import sys; print(f'PYTHONPATH: {os.environ.get(\"PYTHONPATH\")}'); import src.mcp; print('✓ src.mcp imported successfully')"
]

result = subprocess.run(cmd, env=env, capture_output=True, text=True, cwd="/")
if result.returncode == 0:
    print(result.stdout)
else:
    print(f"✗ Failed: {result.stderr}")

# Test -m flag behavior
print("\n--- Testing python -m src.mcp ---")
cmd = [
    "/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python",
    "-m", "src.mcp"
]

# From project root
result = subprocess.run(
    cmd,
    cwd="/Users/douglas.mason/Documents/GitHub/mlb-qbench",
    capture_output=True,
    text=True
)
print(f"From project root: {'✓ Success' if result.returncode == 0 else '✗ Failed'}")
if result.stderr:
    print(f"  Error: {result.stderr}")

# From home directory  
result = subprocess.run(
    cmd,
    cwd="/Users/douglas.mason",
    capture_output=True,
    text=True
)
print(f"From home directory: {'✓ Success' if result.returncode == 0 else '✗ Failed'}")
if result.stderr:
    print(f"  Error: {result.stderr}")