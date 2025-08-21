#!/bin/bash

# Script to stop current migration and restart with optimized version

echo "=== Migration Restart Helper ==="
echo ""

# Check if migration is running
MIGRATION_PID=$(ps aux | grep "migrate_from_sqlite.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$MIGRATION_PID" ]; then
    echo "Found running migration with PID: $MIGRATION_PID"
    echo "Stopping current migration..."
    kill -INT $MIGRATION_PID
    sleep 2
    
    # Force kill if still running
    if ps -p $MIGRATION_PID > /dev/null; then
        echo "Force stopping migration..."
        kill -9 $MIGRATION_PID
    fi
    echo "Migration stopped."
else
    echo "No migration currently running."
fi

echo ""
echo "Checking current database status..."

# Get current count from database
python3 << 'EOF'
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def check_status():
    import asyncpg
    
    dsn = os.getenv("DATABASE_URL", "postgresql://douglas.mason@localhost/mlb_qbench")
    conn = await asyncpg.connect(dsn)
    
    try:
        # Get current counts
        doc_count = await conn.fetchval("SELECT COUNT(*) FROM test_documents")
        step_count = await conn.fetchval("SELECT COUNT(*) FROM test_steps")
        
        # Get last inserted ID
        last_id = await conn.fetchval("SELECT MAX(test_case_id) FROM test_documents")
        
        print(f"Current database status:")
        print(f"  Documents: {doc_count}")
        print(f"  Steps: {step_count}")
        print(f"  Last test_case_id: {last_id}")
        
        return last_id
        
    finally:
        await conn.close()

last_id = asyncio.run(check_status())
EOF

echo ""
echo "Options:"
echo "1. Start fresh migration (clear database and start from beginning)"
echo "2. Resume migration from where it stopped"
echo "3. Test optimized migration with 1000 records"
echo "4. Exit"
echo ""
read -p "Choose option (1-4): " choice

case $choice in
    1)
        echo "Clearing database and starting fresh migration..."
        python scripts/clear_db.py
        echo ""
        echo "Starting optimized migration..."
        python scripts/migrate_optimized.py --batch-size 500 --checkpoint-interval 5000
        ;;
    2)
        read -p "Enter the test ID to resume from (or press Enter to auto-detect): " resume_id
        if [ -z "$resume_id" ]; then
            # Try to get last ID from database
            resume_id=$(python3 -c "
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

async def get_last_id():
    import asyncpg
    dsn = os.getenv('DATABASE_URL', 'postgresql://douglas.mason@localhost/mlb_qbench')
    conn = await asyncpg.connect(dsn)
    last_id = await conn.fetchval('SELECT MAX(test_case_id) FROM test_documents')
    await conn.close()
    return last_id or 0

print(asyncio.run(get_last_id()))
")
        fi
        echo "Resuming migration from test ID: $resume_id"
        python scripts/migrate_optimized.py --resume-from $resume_id --batch-size 500 --checkpoint-interval 5000
        ;;
    3)
        echo "Testing optimized migration with 1000 records..."
        python scripts/clear_db.py
        python scripts/migrate_optimized.py --limit 1000 --batch-size 100
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac