#!/bin/bash

# Full TestRail to PostgreSQL migration script
# Migrates all 104,121 test cases with progress tracking and resume capability

set -e

echo "=========================================="
echo "MLB QBench TestRail Migration"
echo "=========================================="
echo ""
echo "This script will migrate 104,121 test cases from TestRail SQLite to PostgreSQL."
echo "The migration includes generating embeddings for each test, which will:"
echo "  - Take approximately 2-4 hours to complete"
echo "  - Use OpenAI API quota (approximately $50-100 in API costs)"
echo "  - Require stable internet connection"
echo ""
echo "The migration is resumable - if it fails, you can restart from where it left off."
echo ""

# Check environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY environment variable is not set"
    echo "Please set it with: export OPENAI_API_KEY=your-key"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "WARNING: DATABASE_URL not set, using default: postgresql://douglas.mason@localhost/mlb_qbench"
    export DATABASE_URL="postgresql://douglas.mason@localhost/mlb_qbench"
fi

# Check if testrail_data.db exists
if [ ! -f "testrail_data.db" ]; then
    echo "ERROR: testrail_data.db not found in current directory"
    exit 1
fi

# Ask for confirmation
read -p "Do you want to proceed with the full migration? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Migration cancelled."
    exit 0
fi

# Check if there's a previous migration
echo ""
echo "Checking for existing data..."
python -c "
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.db.postgres_vector import PostgresVectorDB

async def check():
    db = PostgresVectorDB('$DATABASE_URL')
    await db.initialize()
    
    async with db.pool.acquire() as conn:
        count = await conn.fetchval('SELECT COUNT(*) FROM test_documents')
        if count > 0:
            print(f'WARNING: Database already contains {count:,} test documents.')
            print('You may want to clear the database first with: make postgres-clean')
            print('Or use --resume-from flag to continue from a specific test ID')
        else:
            print('Database is empty, ready for migration.')
    
    await db.close()

asyncio.run(check())
"

echo ""
echo "Starting migration..."
echo "You can monitor progress in the terminal."
echo "If the migration fails, note the last processed ID and use:"
echo "  python scripts/migrate_from_sqlite.py --resume-from <ID>"
echo ""

# Run the migration with reasonable batch size
# Using batch size of 100 for balance between speed and memory usage
python scripts/migrate_from_sqlite.py \
    --postgres-dsn "$DATABASE_URL" \
    --batch-size 100 \
    2>&1 | tee migration.log

echo ""
echo "=========================================="
echo "Migration complete!"
echo "Check migration.log for details."
echo "=========================================="

# Show final statistics
echo ""
python -c "
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from src.db.postgres_vector import PostgresVectorDB

async def stats():
    db = PostgresVectorDB('$DATABASE_URL')
    await db.initialize()
    
    async with db.pool.acquire() as conn:
        doc_count = await conn.fetchval('SELECT COUNT(*) FROM test_documents')
        step_count = await conn.fetchval('SELECT COUNT(*) FROM test_steps')
        
        print(f'Final database statistics:')
        print(f'  - Test documents: {doc_count:,}')
        print(f'  - Test steps: {step_count:,}')
    
    await db.close()

asyncio.run(stats())
"