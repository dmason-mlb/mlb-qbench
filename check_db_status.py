#!/usr/bin/env python3
"""Check the current database status and test counts."""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def check_database():
    """Check database status and counts."""
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        print("ERROR: DATABASE_URL environment variable not set")
        return
    
    print(f"Connecting to database...")
    
    try:
        conn = await asyncpg.connect(dsn)
        
        # Get basic counts
        doc_count = await conn.fetchval("SELECT COUNT(*) FROM test_documents")
        step_count = await conn.fetchval("SELECT COUNT(*) FROM test_steps")
        
        # Get detailed statistics
        stats = await conn.fetchrow("""
            SELECT 
                COUNT(DISTINCT test_case_id) as unique_tests,
                COUNT(DISTINCT uid) as unique_uids,
                COUNT(DISTINCT jira_key) as tests_with_jira,
                COUNT(*) FILTER (WHERE embedding IS NOT NULL) as tests_with_embeddings,
                COUNT(*) FILTER (WHERE embedding IS NULL) as tests_without_embeddings,
                MIN(test_case_id) as min_id,
                MAX(test_case_id) as max_id,
                COUNT(DISTINCT priority) as priority_types,
                COUNT(DISTINCT test_type) as test_types
            FROM test_documents
        """)
        
        # Get size information
        size_info = await conn.fetchrow("""
            SELECT 
                pg_size_pretty(pg_database_size('mlb_qbench')) as db_size,
                pg_size_pretty(pg_total_relation_size('test_documents')) as docs_table_size,
                pg_size_pretty(pg_total_relation_size('test_steps')) as steps_table_size
        """)
        
        # Get sample of test types and priorities
        test_types = await conn.fetch("""
            SELECT test_type, COUNT(*) as count 
            FROM test_documents 
            WHERE test_type IS NOT NULL
            GROUP BY test_type 
            ORDER BY count DESC
            LIMIT 10
        """)
        
        priorities = await conn.fetch("""
            SELECT priority, COUNT(*) as count 
            FROM test_documents 
            WHERE priority IS NOT NULL
            GROUP BY priority 
            ORDER BY count DESC
        """)
        
        print("\n" + "="*60)
        print("DATABASE STATUS REPORT")
        print("="*60)
        
        print(f"\n📊 DOCUMENT COUNTS:")
        print(f"  Total documents:        {doc_count:,}")
        print(f"  Unique test case IDs:   {stats['unique_tests']:,}")
        print(f"  Unique UIDs:            {stats['unique_uids']:,}")
        print(f"  Total steps:            {step_count:,}")
        
        print(f"\n🔢 TEST ID RANGE:")
        print(f"  Minimum ID: {stats['min_id']:,}")
        print(f"  Maximum ID: {stats['max_id']:,}")
        
        print(f"\n🏷️  METADATA:")
        print(f"  Tests with JIRA keys:   {stats['tests_with_jira']:,}")
        print(f"  Tests with embeddings:  {stats['tests_with_embeddings']:,}")
        print(f"  Tests without embeddings: {stats['tests_without_embeddings']:,}")
        
        print(f"\n📂 TEST TYPES:")
        for row in test_types:
            print(f"  {row['test_type'] or 'NULL':20s}: {row['count']:,}")
        
        print(f"\n🎯 PRIORITIES:")
        for row in priorities:
            print(f"  {row['priority'] or 'NULL':20s}: {row['count']:,}")
        
        print(f"\n💾 DATABASE SIZE:")
        print(f"  Total database size:    {size_info['db_size']}")
        print(f"  Documents table size:   {size_info['docs_table_size']}")
        print(f"  Steps table size:       {size_info['steps_table_size']}")
        
        print(f"\n📈 MIGRATION PROGRESS:")
        print(f"  Original TestRail tests: 104,121")
        print(f"  Current coverage:        {(doc_count/104121)*100:.1f}%")
        print(f"  Migration status:        {'COMPLETE' if doc_count >= 104000 else 'INCOMPLETE'}")
        
        if doc_count < 104000:
            missing = 104121 - doc_count
            print(f"  Missing tests:           {missing:,}")
        
        await conn.close()
        
    except Exception as e:
        print(f"ERROR: Failed to connect to database: {e}")
        print(f"DSN: {dsn}")

if __name__ == "__main__":
    asyncio.run(check_database())