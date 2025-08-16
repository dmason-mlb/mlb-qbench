#!/bin/bash

# PostgreSQL + pgvector setup script for MLB QBench
# Requires PostgreSQL 15+ and sudo access

set -e

echo "=== PostgreSQL + pgvector Setup for MLB QBench ==="
echo

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL is not installed. Installing PostgreSQL 15..."
    
    # Detect OS and install PostgreSQL
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install postgresql@15
            brew services start postgresql@15
        else
            echo "Error: Homebrew not found. Please install PostgreSQL 15 manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        sudo apt-get update
        sudo apt-get install -y postgresql-15 postgresql-server-dev-15
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    else
        echo "Unsupported OS. Please install PostgreSQL 15 manually."
        exit 1
    fi
fi

echo "PostgreSQL is installed."

# Install pgvector extension
echo "Installing pgvector extension..."

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS with Homebrew
    if command -v brew &> /dev/null; then
        brew install pgvector
    else
        # Manual installation
        cd /tmp
        git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git
        cd pgvector
        make
        sudo make install
        cd -
    fi
else
    # Linux manual installation
    cd /tmp
    git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git
    cd pgvector
    make
    sudo make install
    cd -
fi

echo "pgvector extension installed."

# Create database and enable extension
echo "Creating mlb_qbench database..."

# Check if database exists
if psql -U postgres -lqt | cut -d \| -f 1 | grep -qw mlb_qbench; then
    echo "Database mlb_qbench already exists."
else
    createdb -U postgres mlb_qbench || sudo -u postgres createdb mlb_qbench
    echo "Database mlb_qbench created."
fi

# Enable pgvector extension
psql -U postgres -d mlb_qbench -c "CREATE EXTENSION IF NOT EXISTS vector;" || \
    sudo -u postgres psql -d mlb_qbench -c "CREATE EXTENSION IF NOT EXISTS vector;"

echo "pgvector extension enabled."

# Set optimal PostgreSQL configuration for vector operations
echo "Optimizing PostgreSQL configuration for vector operations..."

cat << EOF > /tmp/pgvector_config.sql
-- Optimize for vector operations
ALTER SYSTEM SET shared_buffers = '1GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET effective_cache_size = '4GB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET max_parallel_maintenance_workers = 4;

-- Reload configuration
SELECT pg_reload_conf();
EOF

psql -U postgres -d mlb_qbench -f /tmp/pgvector_config.sql || \
    sudo -u postgres psql -d mlb_qbench -f /tmp/pgvector_config.sql

echo "PostgreSQL configuration optimized."

# Test pgvector functionality
echo "Testing pgvector functionality..."

psql -U postgres -d mlb_qbench -c "SELECT vector_version();" || \
    sudo -u postgres psql -d mlb_qbench -c "SELECT vector_version();"

echo
echo "=== Setup Complete ==="
echo "Database: mlb_qbench"
echo "Extension: pgvector"
echo "Connection string: postgresql://postgres@localhost/mlb_qbench"
echo
echo "Next steps:"
echo "1. Run: make db-schema   # To create tables and indexes"
echo "2. Update .env with DATABASE_URL=postgresql://postgres@localhost/mlb_qbench"