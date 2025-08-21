#!/usr/bin/env python3
"""Find tests that exist in SQLite but not in PostgreSQL."""

import asyncio
import sqlite3
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def find_missing_tests():
    # Get all test IDs from SQLite
    sqlite_conn = sqlite3.connect('testrail_data.db')
    cursor = sqlite_conn.cursor()
    cursor.execute('SELECT id FROM cases ORDER BY id')
    sqlite_ids = set(row[0] for row in cursor.fetchall())
    sqlite_conn.close()
    
    print(f"SQLite has {len(sqlite_ids):,} test IDs")
    
    # Get all test IDs from PostgreSQL
    pg_conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    pg_rows = await pg_conn.fetch('SELECT uid FROM test_documents')
    pg_ids = set()
    for row in pg_rows:
        # Extract numeric ID from uid (e.g., "testrail_123" -> 123)
        uid = row['uid']
        if uid.startswith('testrail_'):
            try:
                pg_ids.add(int(uid.replace('testrail_', '')))
            except ValueError:
                pass
    await pg_conn.close()
    
    print(f"PostgreSQL has {len(pg_ids):,} test IDs")
    
    # Find missing IDs
    missing_ids = sorted(sqlite_ids - pg_ids)
    print(f"\nMissing {len(missing_ids)} tests from PostgreSQL:")
    
    # Write missing IDs to file
    with open('missing_test_ids.txt', 'w') as f:
        for test_id in missing_ids:
            f.write(f"{test_id}\n")
    
    # Show first and last 10
    if missing_ids:
        print(f"First 10: {missing_ids[:10]}")
        print(f"Last 10: {missing_ids[-10:]}")
        print(f"\nWrote all {len(missing_ids)} missing IDs to missing_test_ids.txt")
    
    return missing_ids

if __name__ == "__main__":
    missing = asyncio.run(find_missing_tests())