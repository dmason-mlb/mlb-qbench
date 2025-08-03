#!/Users/douglas.mason/Documents/GitHub/mlb-qbench/venv/bin/python
"""MCP wrapper with virtual environment shebang for direct execution.

This specialized wrapper script uses a virtual environment shebang to ensure
the MCP server runs with the correct Python interpreter and environment. Unlike
other wrappers that rely on the system Python, this script explicitly uses the
virtual environment's Python interpreter through its shebang line.

Key features:
1. Virtual environment shebang for direct execution
2. Automatic working directory configuration
3. Python path setup for module imports
4. Import verification with detailed error reporting
5. Graceful error handling with diagnostic output

The virtual environment shebang approach ensures:
- Correct Python interpreter is always used
- Virtual environment packages are available
- No need for activation scripts
- Works when executed directly (./mcp_venv_wrapper.py)

This wrapper is ideal when:
- The script needs to be executable without 'python' prefix
- Virtual environment isolation is critical
- Claude Desktop or other tools execute scripts directly
- Consistent environment is required regardless of shell state

Error handling includes:
- Import failure detection
- Diagnostic information to stderr
- Working directory and Python path logging
- Non-zero exit code for tool integration

Dependencies:
    - Virtual environment at /Users/douglas.mason/Documents/GitHub/mlb-qbench/venv
    - src.mcp.server: The main MCP server module
    - asyncio: For running the async server

Usage:
    ./mcp_venv_wrapper.py  (direct execution)
    python mcp_venv_wrapper.py  (explicit Python)

Note: The shebang path is hardcoded to the specific virtual environment location.
"""

import os
import sys
import asyncio

# Establish environment paths
# Script directory is used as the project root since this wrapper is at root level
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir  # This script is in the project root

# Set working directory to project root for consistent relative paths
os.chdir(project_root)

# Configure Python module search path
# This allows importing from src/ without package installation
sys.path.insert(0, project_root)

# Verify the MCP server module can be imported before attempting to run
# This provides early failure detection with helpful diagnostics
try:
    from src.mcp.server import main
except ImportError as e:
    # Log detailed error information to stderr for debugging
    # Claude Desktop and other tools can capture this for diagnostics
    print(f"Import error: {e}", file=sys.stderr)
    print(f"Working directory: {os.getcwd()}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    sys.exit(1)

# Launch the MCP server if import was successful
if __name__ == "__main__":
    asyncio.run(main())