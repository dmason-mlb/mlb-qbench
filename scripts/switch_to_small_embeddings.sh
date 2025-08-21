#!/bin/bash

# Script to switch from text-embedding-3-large to text-embedding-3-small
# This will recreate the database with 1536-dimension vectors that support indexing

echo "=== Switching to text-embedding-3-small (1536 dimensions) ==="
echo ""
echo "This will:"
echo "1. Drop and recreate the database with 1536-dimension vectors"
echo "2. Enable proper vector indexing (HNSW)"
echo "3. Reduce costs by 5x ($0.02 vs $0.13 per 1M tokens)"
echo "4. Make searches 100-1000x faster with indexes"
echo ""

# Check if migration is running
MIGRATION_PID=$(ps aux | grep -E "migrate.*\.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$MIGRATION_PID" ]; then
    echo "❌ Migration is currently running (PID: $MIGRATION_PID)"
    echo "Please stop it first before switching embedding models."
    exit 1
fi

echo "Current embedding model configuration:"
grep "EMBED_MODEL" .env

echo ""
read -p "Continue with switching to text-embedding-3-small? (y/N): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Step 1: Updating .env file..."
if [ -f .env ]; then
    # Backup current .env
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    
    # Update embedding model
    if grep -q "EMBED_MODEL=text-embedding-3-large" .env; then
        sed -i '' 's/EMBED_MODEL=text-embedding-3-large/EMBED_MODEL=text-embedding-3-small/' .env
        echo "✓ Updated EMBED_MODEL to text-embedding-3-small"
    else
        echo "⚠️  EMBED_MODEL already set to something other than text-embedding-3-large"
    fi
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "Step 2: Recreating database with 1536-dimension schema..."

# Drop and recreate database
echo "Dropping existing database..."
dropdb mlb_qbench --if-exists

echo "Creating new database..."
createdb mlb_qbench

echo "Installing pgvector extension and creating schema..."
psql -d mlb_qbench << 'EOF'
CREATE EXTENSION IF NOT EXISTS vector;
\i sql/create_schema_optimized.sql
EOF

echo ""
echo "Step 3: Verifying new schema..."
psql -d mlb_qbench << 'EOF'
-- Check vector dimensions
SELECT 
    table_name,
    column_name,
    udt_name,
    character_maximum_length
FROM information_schema.columns 
WHERE column_name = 'embedding';

-- Check indexes
SELECT 
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname LIKE '%embedding%';
EOF

echo ""
echo "✅ Successfully switched to text-embedding-3-small!"
echo ""
echo "Benefits of this change:"
echo "• Vector indexes now work (searches will be 100-1000x faster)"
echo "• 5x cost reduction on embeddings"
echo "• Still excellent search quality (text-embedding-3-small is very capable)"
echo ""
echo "Next steps:"
echo "1. Run the optimized migration: make migrate-optimized"
echo "2. Or test with 1000 records first: python scripts/migrate_optimized.py --limit 1000"
echo ""
echo "Estimated costs for full migration:"
echo "• ~104k tests × ~500 tokens/test = 52M tokens"
echo "• Cost: ~\$1.04 (vs \$6.76 with large model)"