#!/usr/bin/env python3
"""Test migration of specific test IDs to understand failures."""

import asyncio
import sqlite3
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import structlog

logger = structlog.get_logger()


async def test_single_migration(test_ids: list[int]):
    """Try to migrate specific test IDs and report detailed errors."""
    
    migrator = OptimizedTestRailMigrator(
        sqlite_path="testrail_data.db",
        batch_size=100,
        checkpoint_interval=1000
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Connect to SQLite
        cursor = migrator.sqlite_conn.cursor()
        
        for test_id in test_ids:
            print(f"\n{'='*60}")
            print(f"Testing migration of test ID: {test_id}")
            print('='*60)
            
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
                continue
            
            # Print raw data
            print(f"\nRaw SQLite data:")
            print(f"  id: {row['id']}")
            print(f"  title: {row['title']!r}")
            print(f"  is_automated: {row['is_automated']}")
            print(f"  priority_id: {row['priority_id']}")
            print(f"  suite_id: {row['suite_id']}")
            print(f"  section_id: {row['section_id']}")
            
            if row['custom_fields']:
                try:
                    custom = json.loads(row['custom_fields'])
                    print(f"  custom_fields: {json.dumps(custom, indent=2)[:500]}")
                except:
                    print(f"  custom_fields: INVALID JSON")
            
            # Try to convert to TestDoc
            try:
                test_doc = migrator.convert_to_test_doc(row)
                print(f"\n✓ Successfully converted to TestDoc")
                print(f"  uid: {test_doc.uid}")
                print(f"  testType: {test_doc.testType}")
                print(f"  priority: {test_doc.priority}")
                
                # Try to insert (without actually doing it)
                print(f"\n✓ TestDoc validation passed - ready for insertion")
                
            except Exception as e:
                print(f"\n✗ FAILED to convert to TestDoc:")
                print(f"  Error type: {type(e).__name__}")
                print(f"  Error message: {str(e)}")
                
                # Try to identify the specific field causing issues
                if "validation error" in str(e).lower():
                    print(f"\n  Validation error details:")
                    print(f"  {str(e)}")
    
    finally:
        await migrator.close()


async def main():
    """Test specific problematic test IDs."""
    
    # Test a sample of each category
    test_ids = [
        # First automated test that failed re-migration
        34372537,
        # First manual test that was never attempted
        30696481,
        # Last automated test that failed
        34780701,
        # Last manual test that was never attempted  
        30696580,
    ]
    
    print("Testing migration of sample problematic tests...")
    await test_single_migration(test_ids)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    asyncio.run(main())