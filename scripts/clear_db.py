#!/usr/bin/env python3
"""Clear all data from PostgreSQL database tables."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.db.postgres_vector import PostgresVectorDB


async def clear_database():
    """Clear all data from database tables."""
    db = PostgresVectorDB()
    await db.initialize()
    
    async with db.pool.acquire() as conn:
        # Clear both tables
        await conn.execute('TRUNCATE TABLE test_documents CASCADE')
        await conn.execute('TRUNCATE TABLE test_steps CASCADE')
        
        # Get counts to verify
        doc_count = await conn.fetchval('SELECT COUNT(*) FROM test_documents')
        step_count = await conn.fetchval('SELECT COUNT(*) FROM test_steps')
        
        print(f'✓ Database cleared successfully')
        print(f'  Test documents: {doc_count}')
        print(f'  Test steps: {step_count}')
    
    await db.close()


if __name__ == "__main__":
    asyncio.run(clear_database())