#!/usr/bin/env python3
"""Debug insertion of a single test to understand the failure."""

import asyncio
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import structlog

logger = structlog.get_logger()


async def debug_insert_test(test_id: int):
    """Try to insert a single test and capture detailed error."""
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    migrator = OptimizedTestRailMigrator(
        sqlite_path="testrail_data.db",
        postgres_dsn=os.getenv("DATABASE_URL"),
        batch_size=1,
        checkpoint_interval=1000
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Connect to SQLite
        cursor = migrator.sqlite_conn.cursor()
        
        # Get test from SQLite
        query = """
            SELECT 
                id, suite_id, section_id, project_id, priority_id,
                title, preconditions, steps_separated, custom_fields,
                jiras, refs, comment, is_automated, created_on, updated_on
            FROM cases
            WHERE id = ?
        """
        
        cursor.execute(query, (test_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"Test {test_id} not found in SQLite")
            return
        
        print(f"Processing test {test_id}: {row['title'][:50]}...")
        
        # Convert to TestDoc
        try:
            test_doc = migrator.convert_to_test_doc(row)
            print(f"✓ Converted to TestDoc successfully")
            print(f"  UID: {test_doc.uid}")
            print(f"  Type: {test_doc.testType}")
        except Exception as e:
            print(f"✗ Failed to convert: {e}")
            return
        
        # Try to insert using the batch insert method
        try:
            result = await migrator.pg_db.batch_insert_documents_optimized(
                [test_doc],
                migrator.embedder,
                doc_batch_size=1,
                embedding_batch_size=1
            )
            
            print(f"\nInsertion result:")
            print(f"  Inserted: {result['inserted']}")
            print(f"  Failed: {result['failed']}")
            print(f"  Skipped: {result['skipped']}")
            
            if result['failed'] > 0:
                print(f"\n✗ INSERTION FAILED")
            else:
                print(f"\n✓ INSERTION SUCCESSFUL")
                
        except Exception as e:
            print(f"\n✗ Insertion error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    finally:
        await migrator.close()


async def main():
    """Test insertion of a problematic test."""
    
    # Test with the first missing automated test
    test_id = 34372537
    
    print(f"Testing insertion of test ID {test_id}...")
    await debug_insert_test(test_id)


if __name__ == "__main__":
    asyncio.run(main())