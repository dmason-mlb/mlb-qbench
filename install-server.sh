#!/bin/bash
set -euo pipefail

# ============================================================================
# MLB QBench MCP Server Setup Script
#
# A platform-agnostic setup script that works on macOS, Linux, and WSL.
# Handles environment setup, dependency installation, and configuration.
# ============================================================================

# Initialize pyenv if available (do this early)
if [[ -d "$HOME/.pyenv" ]]; then
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    if command -v pyenv &> /dev/null; then
        eval "$(pyenv init --path)" 2>/dev/null || true
        eval "$(pyenv init -)" 2>/dev/null || true
    fi
fi

# ----------------------------------------------------------------------------
# Constants and Configuration
# ----------------------------------------------------------------------------

# Colors for output (ANSI codes work on all platforms)
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly RED='\033[0;31m'
readonly NC='\033[0m' # No Color

# Configuration
readonly VENV_PATH=".venv"

# ----------------------------------------------------------------------------
# Utility Functions
# ----------------------------------------------------------------------------

# Print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1" >&2
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1" >&2
}

print_info() {
    echo -e "${YELLOW}$1${NC}" >&2
}

# Get the script's directory (works on all platforms)
get_script_dir() {
    cd "$(dirname "$0")" && pwd
}

# Clear Python cache files to prevent import issues
clear_python_cache() {
    print_info "Clearing Python cache files..."
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    print_success "Python cache cleared"
}

# ----------------------------------------------------------------------------
# Platform Detection Functions
# ----------------------------------------------------------------------------

# Get cross-platform Python executable path from venv
get_venv_python_path() {
    local venv_path="$1"

    # Check for both Unix and Windows Python executable paths
    if [[ -f "$venv_path/bin/python" ]]; then
        echo "$venv_path/bin/python"
    elif [[ -f "$venv_path/Scripts/python.exe" ]]; then
        echo "$venv_path/Scripts/python.exe"
    else
        return 1  # No Python executable found
    fi
}

# Detect the operating system
detect_os() {
    case "$OSTYPE" in
        darwin*)  echo "macos" ;;
        linux*)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                echo "wsl"
            else
                echo "linux"
            fi
            ;;
        msys*|cygwin*|win32) echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

# Get Claude config path based on platform
get_claude_config_path() {
    local os_type=$(detect_os)

    case "$os_type" in
        macos)
            echo "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
            ;;
        linux)
            echo "$HOME/.config/Claude/claude_desktop_config.json"
            ;;
        wsl)
            local win_appdata
            if command -v wslvar &> /dev/null; then
                win_appdata=$(wslvar APPDATA 2>/dev/null)
            fi

            if [[ -n "$win_appdata" ]]; then
                echo "$(wslpath "$win_appdata")/Claude/claude_desktop_config.json"
            else
                print_warning "Could not determine Windows user path automatically. Please ensure APPDATA is set correctly or provide the full path manually."
                echo "/mnt/c/Users/$USER/AppData/Roaming/Claude/claude_desktop_config.json"
            fi
            ;;
        windows)
            echo "$APPDATA/Claude/claude_desktop_config.json"
            ;;
        *)
            echo ""
            ;;
    esac
}

# Get Cursor config path (cross-platform)
get_cursor_config_path() {
    echo "$HOME/.cursor/mcp.json"
}

# ----------------------------------------------------------------------------
# Python Environment Functions
# ----------------------------------------------------------------------------

# Find suitable Python command
find_python() {
    # Pyenv should already be initialized at script start, but check if .python-version exists
    if [[ -f ".python-version" ]] && command -v pyenv &> /dev/null; then
        # Ensure pyenv respects the local .python-version
        pyenv local &>/dev/null || true
    fi

    # Prefer Python 3.12 for best compatibility
    local python_cmds=("python3.12" "python3.13" "python3.11" "python3.10" "python3" "python" "py")

    for cmd in "${python_cmds[@]}"; do
        if command -v "$cmd" &> /dev/null; then
            local version=$($cmd --version 2>&1)
            if [[ $version =~ Python\ ([0-9]+)\.([0-9]+)\.([0-9]+) ]]; then
                local major_version=${BASH_REMATCH[1]}
                local minor_version=${BASH_REMATCH[2]}
                local patch_version=${BASH_REMATCH[3]}

                # Check minimum version (3.10) for better library compatibility
                if [[ $major_version -eq 3 && $minor_version -ge 10 ]] || [[ $major_version -gt 3 ]]; then
                    # Verify the command actually exists (important for pyenv)
                    if command -v "$cmd" &> /dev/null; then
                        echo "$cmd"
                        print_success "Found Python: $version"

                        # Recommend Python 3.12
                        if [[ $major_version -eq 3 && $minor_version -ne 12 ]]; then
                            print_info "Note: Python 3.12 is recommended for best compatibility."
                        fi

                        return 0
                    fi
                fi
            fi
        fi
    done

    print_error "Python 3.10+ not found. MCP Atlassian requires Python 3.10+."
    echo "" >&2

    local os_type=$(detect_os)
    if [[ "$os_type" == "macos" ]]; then
        echo "To install Python:" >&2
        echo "  brew install python@3.12" >&2
    elif [[ "$os_type" == "linux" || "$os_type" == "wsl" ]]; then
        echo "To install Python:" >&2
        echo "  Ubuntu/Debian: sudo apt update && sudo apt install -y python3.12 python3.12-venv python3.12-pip" >&2
        echo "  RHEL/CentOS:   sudo dnf install -y python3.12 python3.12-venv python3.12-pip" >&2
        echo "  Arch:          sudo pacman -S python python-pip" >&2
    fi
    echo "" >&2

    return 1
}

# Setup virtual environment
setup_venv() {
    local python_cmd="$1"
    local venv_python=""

    # Create venv if it doesn't exist
    if [[ ! -d "$VENV_PATH" ]]; then
        print_info "Creating isolated environment..."

        # Try creating virtual environment
        if $python_cmd -m venv "$VENV_PATH" >/dev/null 2>&1; then
            print_success "Created isolated environment"
        else
            print_error "Failed to create virtual environment"
            echo "" >&2
            echo "Your system may be missing Python development packages." >&2
            echo "Please install python3-venv or python3-dev packages for your system." >&2
            exit 1
        fi
    fi

    # Get venv Python path based on platform
    venv_python=$(get_venv_python_path "$VENV_PATH")
    if [[ $? -ne 0 ]]; then
        print_error "Virtual environment Python not found"
        exit 1
    fi

    # Verify pip is working
    if ! $venv_python -m pip --version &>/dev/null 2>&1; then
        print_error "pip is not working correctly in the virtual environment"
        echo "" >&2
        echo "Try deleting the virtual environment and running again:" >&2
        echo "  rm -rf $VENV_PATH" >&2
        echo "  ./install-server.sh" >&2
        exit 1
    fi

    print_success "Virtual environment ready with pip"

    # Convert to absolute path for MCP registration
    local abs_venv_python=$(cd "$(dirname "$venv_python")" && pwd)/$(basename "$venv_python")
    echo "$abs_venv_python"
    return 0
}

# Check if package is installed
check_package() {
    local python_cmd="$1"
    local package="$2"
    $python_cmd -c "import $package" 2>/dev/null
}

# Install dependencies using uv
install_dependencies() {
    local python_cmd="$1"

    # Check if uv is available in the venv
    if ! $python_cmd -m pip show uv &>/dev/null; then
        print_info "Installing uv package manager..."
        $python_cmd -m pip install -q uv
        print_success "uv installed"
    fi

    # Check if project dependencies are already installed
    if $python_cmd -c "import src.mcp.server" 2>/dev/null; then
        print_success "Dependencies already installed"
    else
        echo ""
        print_info "Setting up MLB QBench MCP Server..."
        echo "Installing required components:"
        echo "  • MCP protocol library"
        echo "  • PostgreSQL with pgvector support"
        echo "  • AsyncPG for PostgreSQL connections"
        echo "  • OpenAI/Cohere/Vertex embedding providers"
        echo "  • FastAPI and async components"
        echo ""

        # Use uv to install from pyproject.toml
        local install_cmd="$python_cmd -m uv sync --all-extras"

        echo -n "Downloading packages..."
        local install_output

        # Capture both stdout and stderr
        install_output=$($install_cmd 2>&1)
        local exit_code=$?

        if [[ $exit_code -ne 0 ]]; then
            echo -e "\r${RED}✗ Setup failed${NC}                      "
            echo ""
            echo "Installation error:"
            echo "$install_output" | head -20
            echo ""
            echo "Try running manually:"
            echo "  $python_cmd -m uv sync --all-extras"
            return 1
        else
            echo -e "\r${GREEN}✓ Setup complete!${NC}                    "
        fi
    fi

    # Ensure asyncpg is installed for PostgreSQL support
    if ! $python_cmd -m pip show asyncpg &>/dev/null; then
        print_info "Installing asyncpg for PostgreSQL support..."
        $python_cmd -m pip install -q asyncpg
        print_success "asyncpg installed"
    fi

    return 0
}

# ----------------------------------------------------------------------------
# Environment Configuration Functions
# ----------------------------------------------------------------------------

# Create the MCP server wrapper script
create_mcp_wrapper() {
    local wrapper_path="run_mcp_server.py"
    
    if [[ -f "$wrapper_path" ]]; then
        print_success "MCP wrapper script already exists"
        return 0
    fi
    
    print_info "Creating MCP server wrapper script..."
    
    cat > "$wrapper_path" << 'EOF'
#!/usr/bin/env python
"""Direct runner for MCP server that handles imports properly."""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure structlog to use stderr for ALL modules
# This must be done before importing any modules that use structlog
import structlog
structlog.configure(
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
)

from src.mcp.server_postgres import main

if __name__ == "__main__":
    asyncio.run(main())
EOF
    
    # Make the wrapper executable
    chmod +x "$wrapper_path"
    
    print_success "Created MCP wrapper script: $wrapper_path"
    return 0
}

# Setup .env file
setup_env_file() {
    if [[ -f .env ]]; then
        print_success ".env file already exists"
        return 0
    fi

    print_info "Creating .env file with example configuration..."

    cat > .env << 'EOF'
# MLB QBench Configuration

# PostgreSQL Configuration
DATABASE_URL=postgresql://username@localhost/mlb_qbench

# Embedding Provider Configuration
# Choose one provider and configure its settings
EMBED_PROVIDER=openai               # Options: openai, cohere, vertex, azure
EMBED_MODEL=text-embedding-3-small  # 1536 dimensions for pgvector compatibility

# Provider API Keys (set the one you're using)
# OPENAI_API_KEY=your-key-here
# COHERE_API_KEY=your-key-here
# VERTEX_PROJECT=your-project
# AZURE_OPENAI_ENDPOINT=your-endpoint

# Optional: API Authentication (for production)
# MASTER_API_KEY=your-master-key      # Admin access for all operations
# API_KEYS=key1,key2,key3            # Comma-separated list of valid API keys

# Optional: Logging
# LOG_LEVEL=INFO
# LOG_FORMAT=json
EOF

    print_success "Created .env file with example configuration"
    print_warning "Please edit .env and configure your embedding provider credentials!"

    return 0
}

# Safely parse .env file without executing arbitrary code
parse_env_safely() {
    local env_file=".env"
    [[ -f "$env_file" ]] || return 0

    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ $key =~ ^[[:space:]]*# ]] && continue
        [[ -z "$key" ]] && continue

        # Validate key format (only allow alphanumeric and underscore)
        if [[ $key =~ ^[A-Z0-9_]+$ ]]; then
            # Remove inline comments from value
            value=${value%%#*}
            # Trim whitespace
            value=$(echo "$value" | xargs)
            # Remove quotes from value if present
            value=${value#\"}
            value=${value%\"}
            export "$key=$value"
        fi
    done < <(grep -E '^[A-Z0-9_]+=' "$env_file" 2>/dev/null || true)
}

# Validate configuration
validate_config() {
    local has_config=false

    # Safely parse the .env file to check values
    if [[ -f .env ]]; then
        parse_env_safely
    fi

    # Check for PostgreSQL configuration
    if [[ -n "${DATABASE_URL:-}" ]]; then
        print_success "DATABASE_URL configured"
        has_config=true
    else
        # Default to localhost if not configured
        export DATABASE_URL="postgresql://$(whoami)@localhost/mlb_qbench"
        print_info "Using default DATABASE_URL: postgresql://$(whoami)@localhost/mlb_qbench"
        has_config=true
    fi

    # Check for embedding provider configuration
    if [[ -n "${EMBED_PROVIDER:-}" ]]; then
        print_success "EMBED_PROVIDER configured: ${EMBED_PROVIDER}"
        
        # Check for corresponding API key
        case "${EMBED_PROVIDER}" in
            openai)
                if [[ -n "${OPENAI_API_KEY:-}" ]]; then
                    print_success "OpenAI API key configured"
                else
                    has_config=false
                    print_error "OpenAI API key not found!"
                fi
                ;;
            cohere)
                if [[ -n "${COHERE_API_KEY:-}" ]]; then
                    print_success "Cohere API key configured"
                else
                    has_config=false
                    print_error "Cohere API key not found!"
                fi
                ;;
            vertex)
                if [[ -n "${VERTEX_PROJECT:-}" ]]; then
                    print_success "Vertex AI project configured"
                else
                    has_config=false
                    print_error "Vertex AI project not found!"
                fi
                ;;
            azure)
                if [[ -n "${AZURE_OPENAI_ENDPOINT:-}" ]]; then
                    print_success "Azure OpenAI endpoint configured"
                else
                    has_config=false
                    print_error "Azure OpenAI endpoint not found!"
                fi
                ;;
            *)
                has_config=false
                print_error "Unknown embedding provider: ${EMBED_PROVIDER}"
                ;;
        esac
    else
        has_config=false
        print_error "EMBED_PROVIDER not configured!"
    fi

    if [[ "$has_config" == false ]]; then
        print_error "Embedding provider credentials not found in .env!"
        echo "" >&2
        echo "Please edit .env and configure your embedding provider:" >&2
        echo "" >&2
        echo "For OpenAI:" >&2
        echo "  EMBED_PROVIDER=openai" >&2
        echo "  EMBED_MODEL=text-embedding-3-large" >&2
        echo "  OPENAI_API_KEY=your-api-key" >&2
        echo "" >&2
        echo "For Cohere:" >&2
        echo "  EMBED_PROVIDER=cohere" >&2
        echo "  EMBED_MODEL=embed-english-v3.0" >&2
        echo "  COHERE_API_KEY=your-api-key" >&2
        echo "" >&2
        print_info "After adding your credentials, run ./install-server.sh again" >&2
        echo "" >&2
        return 1
    fi

    return 0
}

# ----------------------------------------------------------------------------
# IDE Integration Functions
# ----------------------------------------------------------------------------

# Shared function to update IDE configuration with proper duplicate detection
update_ide_config() {
    local ide_name="$1"
    local config_path="$2"
    local python_cmd="$3"
    local server_args="$4"

    # Create config directory if it doesn't exist
    local config_dir=$(dirname "$config_path")
    mkdir -p "$config_dir" 2>/dev/null || true

    # Handle existing config
    if [[ -f "$config_path" ]]; then
        # Add new config with duplicate detection - consolidated atomic operation
        local temp_file=$(mktemp)
        local python_output=$("$python_cmd" -c "
import json
import sys

config_path = '$config_path'
temp_file = '$temp_file'

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f'ERROR: Could not parse existing config file: {e}')
    print('Backup your config before running this script again.')
    sys.exit(1)

# Ensure mcpServers exists
if 'mcpServers' not in config:
    config['mcpServers'] = {}

# Check if mlb-qbench server already exists
new_config = {
    'command': '$python_cmd',
    'args': ['$server_args'],
}

if 'mlb-qbench' in config['mcpServers']:
    existing_config = config['mcpServers']['mlb-qbench']
    if existing_config == new_config:
        print('ALREADY_CONFIGURED')
        sys.exit(0)
    else:
        print('UPDATING_EXISTING')
        print('Old config:', json.dumps(existing_config, indent=2))
        print('New config:', json.dumps(new_config, indent=2))
else:
    print('ADDING_NEW')

# Add/update mlb-qbench server
config['mcpServers']['mlb-qbench'] = new_config

# Write to temp file atomically
try:
    with open(temp_file, 'w') as f:
        json.dump(config, f, indent=2)
    print('SUCCESS')
except Exception as e:
    print(f'ERROR: Failed to write config: {e}')
    sys.exit(1)
" 2>&1)

        local python_exit_code=$?

        # Handle different scenarios based on Python output
        if [[ "$python_output" == "ALREADY_CONFIGURED" ]]; then
            print_success "$ide_name configuration is already up to date"
            echo "  Config: $config_path"
            rm -f "$temp_file" 2>/dev/null || true
            return 0
        elif echo "$python_output" | grep -q "UPDATING_EXISTING"; then
            print_info "Updating existing $ide_name 'mlb-qbench' server configuration..."
            echo "  Previous configuration will be overwritten"
        elif echo "$python_output" | grep -q "ADDING_NEW"; then
            print_info "Adding 'mlb-qbench' server to existing $ide_name configuration..."
        elif echo "$python_output" | grep -q "ERROR:"; then
            print_error "Python configuration error:"
            echo "$python_output" >&2
            rm -f "$temp_file" 2>/dev/null || true
            return 1
        else
            print_info "Updating existing $ide_name config..."
        fi

        # Move temp file to final location if Python succeeded
        if [[ $python_exit_code -eq 0 ]] && [[ -f "$temp_file" ]] && mv "$temp_file" "$config_path"; then
            print_success "Successfully configured $ide_name"
            echo "  Config: $config_path"
            echo "  Restart $ide_name to use the new MCP server"
        else
            rm -f "$temp_file" 2>/dev/null || true
            print_error "Failed to update $ide_name config"
            echo "Manual config location: $config_path"
            echo "Add this configuration:"
            cat << EOF
{
  "mcpServers": {
    "mlb-qbench": {
      "command": "$python_cmd",
      "args": ["$server_args"]
    }
  }
}
EOF
        fi

    else
        print_info "Creating new $ide_name config..."
        cat > "$config_path" << EOF
{
  "mcpServers": {
    "mlb-qbench": {
      "command": "$python_cmd",
      "args": ["$server_args"]
    }
  }
}
EOF

        if [[ $? -eq 0 ]]; then
            print_success "Successfully configured $ide_name"
            echo "  Config: $config_path"
            echo "  Restart $ide_name to use the new MCP server"
        else
            print_error "Failed to create $ide_name config"
            echo "Manual config location: $config_path"
            echo "Add this configuration:"
            cat << EOF
{
  "mcpServers": {
    "mlb-qbench": {
      "command": "$python_cmd",
      "args": ["$server_args"]
    }
  }
}
EOF
        fi
    fi
}

# Check and update Claude Desktop configuration
check_claude_desktop_integration() {
    local python_cmd="$1"
    local server_args="$2"

    local config_path=$(get_claude_config_path)
    if [[ -z "$config_path" ]]; then
        print_warning "Unable to determine Claude Desktop config path for this platform"
        return 0
    fi

    echo ""
    read -p "Configure MLB QBench MCP Server for Claude Desktop? (Y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Skipping Claude Desktop integration"
        return 0
    fi

    # Use shared configuration function
    update_ide_config "Claude Desktop" "$config_path" "$python_cmd" "$server_args"
}

# Check and update Cursor IDE configuration
check_cursor_ide_integration() {
    local python_cmd="$1"
    local server_args="$2"

    local config_path=$(get_cursor_config_path)

    echo ""
    read -p "Configure MLB QBench MCP Server for Cursor IDE? (Y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        print_info "Skipping Cursor IDE integration"
        return 0
    fi

    # Use shared configuration function
    update_ide_config "Cursor IDE" "$config_path" "$python_cmd" "$server_args"
}

# Display configuration instructions
display_config_instructions() {
    local python_cmd="$1"
    local server_args="$2"

    echo ""
    local config_header="MLB QBENCH MCP SERVER CONFIGURATION"
    echo "===== $config_header ====="
    printf '%*s\n' "$((${#config_header} + 12))" | tr ' ' '='
    echo ""
    echo "To use MLB QBench MCP Server with your Claude clients:"
    echo ""

    print_info "1. For Claude Desktop:"
    echo "   Add this configuration to your Claude Desktop config file:"
    echo ""
    cat << EOF
   {
     "mcpServers": {
       "mlb-qbench": {
         "command": "$python_cmd",
         "args": ["$server_args"]
       }
     }
   }
EOF

    # Show platform-specific config location
    local config_path=$(get_claude_config_path)
    if [[ -n "$config_path" ]]; then
        echo ""
        print_info "   Config file location:"
        echo -e "   ${YELLOW}$config_path${NC}"
    fi

    echo ""
    print_info "2. For Cursor IDE:"
    echo "   Add this configuration to your Cursor IDE config file:"
    echo ""
    cat << EOF
   {
     "mcpServers": {
       "mlb-qbench": {
         "command": "$python_cmd",
         "args": ["$server_args"]
       }
     }
   }
EOF

    local cursor_config_path=$(get_cursor_config_path)
    echo ""
    print_info "   Config file location:"
    echo -e "   ${YELLOW}$cursor_config_path${NC}"
    echo ""

    print_info "3. Restart Claude Desktop/Cursor IDE after updating config files"
    echo ""

    print_info "4. For FastMCP CLI:"
    echo -e "   ${GREEN}fastmcp run mlb-qbench${NC}"
    echo ""
}

# Display setup instructions
display_setup_instructions() {
    local python_cmd="$1"
    local server_args="$2"

    echo ""
    local setup_header="SETUP COMPLETE"
    echo "===== $setup_header ====="
    printf '%*s\n' "$((${#setup_header} + 12))" | tr ' ' '='
    echo ""
    print_success "MLB QBench MCP Server is ready to use!"
    echo ""
    print_info "Quick Test:"
    echo "  $python_cmd run_mcp_server.py"
    echo ""
    print_info "With environment file:"
    echo "  $python_cmd run_mcp_server.py --env-file .env"
    echo ""
    print_info "With verbose logging:"
    echo "  $python_cmd run_mcp_server.py -vv"
    echo ""
    print_info "Start PostgreSQL (if not running):"
    echo "  make postgres-setup"
    echo ""
    print_info "FastMCP CLI:"
    echo "  fastmcp run mlb-qbench"
    echo ""
}

# ----------------------------------------------------------------------------
# Main Function
# ----------------------------------------------------------------------------

# Show help message
show_help() {
    local header="🔧 MLB QBench MCP Server Setup"
    echo "$header"
    printf '%*s\n' "${#header}" | tr ' ' '='
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -c, --config    Show configuration instructions for Claude clients"
    echo "  --clear-cache   Clear Python cache and exit (helpful for import issues)"
    echo ""
    echo "Examples:"
    echo "  $0              Setup the MCP server"
    echo "  $0 -c           Show configuration instructions"
    echo "  $0 --clear-cache Clear Python cache (fixes import issues)"
    echo ""
    echo "For more information, visit:"
    echo "  https://github.com/your-org/mlb-qbench"
}

main() {
    # Parse command line arguments
    local arg="${1:-}"

    case "$arg" in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--config)
            # Setup minimal environment to get paths for config display
            echo "Setting up environment for configuration display..."
            echo ""
            local python_cmd
            python_cmd=$(find_python) || exit 1
            python_cmd=$(setup_venv "$python_cmd") || exit 1
            local wrapper_path="$(pwd)/run_mcp_server.py"
            local server_args="$wrapper_path"
            display_config_instructions "$python_cmd" "$server_args"
            exit 0
            ;;
        --clear-cache)
            # Clear cache and exit
            clear_python_cache
            print_success "Cache cleared successfully"
            echo ""
            echo "You can now run './install-server.sh' normally"
            exit 0
            ;;
        "")
            # Normal setup
            ;;
        *)
            print_error "Unknown option: $arg"
            echo "" >&2
            show_help
            exit 1
            ;;
    esac

    # Display header
    local main_header="🔧 MLB QBench MCP Server Setup"
    echo "$main_header"
    printf '%*s\n' "${#main_header}" | tr ' ' '='
    echo ""

    # Check if venv exists
    if [[ ! -d "$VENV_PATH" ]]; then
        echo "Setting up Python environment for first time..."
    fi

    # Step 1: Clear Python cache to prevent import issues
    clear_python_cache

    # Step 2: Setup environment file
    setup_env_file || exit 1

    # Step 3: Create MCP wrapper script
    create_mcp_wrapper || exit 1

    # Step 4: Setup Python environment
    local python_cmd
    python_cmd=$(find_python) || exit 1
    python_cmd=$(setup_venv "$python_cmd") || exit 1

    # Step 5: Install dependencies
    install_dependencies "$python_cmd" || exit 1

    # Step 6: Set server args - use the wrapper script
    local wrapper_path="$(pwd)/run_mcp_server.py"
    local server_args="$wrapper_path"

    # Step 7: Display setup instructions
    display_setup_instructions "$python_cmd" "$server_args"

    # Step 8: Validate configuration (but don't fail if not configured yet)
    echo ""
    print_info "Checking configuration..."
    if validate_config; then
        print_success "Configuration looks good!"
    else
        print_warning "Please configure your embedding provider credentials in .env before using the server"
    fi

    # Step 9: Check Claude Desktop integration
    check_claude_desktop_integration "$python_cmd" "$server_args"

    # Step 10: Check Cursor IDE integration
    check_cursor_ide_integration "$python_cmd" "$server_args"

    echo ""
    echo "To show config: ./install-server.sh -c"
    echo ""
    echo "Happy coding! 🎉"
}

# ----------------------------------------------------------------------------
# Script Entry Point
# ----------------------------------------------------------------------------

# Run main function with all arguments
main "$@"
