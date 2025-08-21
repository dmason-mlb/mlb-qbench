#!/usr/bin/env python3
"""Check if failed tests have long jira_key values."""

import sqlite3
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import asyncio

async def check_jira_key_length():
    """Check jira_key field lengths for failed tests."""
    
    # Read the failed test IDs
    with open("final_failed_test_ids.txt", "r") as f:
        failed_ids = [int(line.strip()) for line in f if line.strip()]
    
    print(f"Checking jira_key lengths for {len(failed_ids)} failed tests...")
    
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
        await migrator.initialize()
        
        # Connect to SQLite
        conn = sqlite3.connect("testrail_data.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        problematic = []
        
        for test_id in failed_ids:
            cursor.execute("""
                SELECT id, jiras, custom_fields
                FROM cases
                WHERE id = ?
            """, (test_id,))
            
            row = cursor.fetchone()
            
            if row:
                # Convert to TestDoc to see the actual jira_key value
                full_row = cursor.execute("""
                    SELECT 
                        id, suite_id, section_id, project_id, priority_id,
                        title, preconditions, steps_separated, custom_fields,
                        jiras, refs, comment, is_automated, created_on, updated_on
                    FROM cases
                    WHERE id = ?
                """, (test_id,)).fetchone()
                
                test_doc = migrator.convert_to_test_doc(full_row)
                
                if test_doc.jiraKey and len(test_doc.jiraKey) > 50:
                    print(f"Test {test_id}: jiraKey = '{test_doc.jiraKey}' ({len(test_doc.jiraKey)} chars) *** TOO LONG ***")
                    problematic.append(test_id)
                elif test_doc.jiraKey:
                    print(f"Test {test_id}: jiraKey = '{test_doc.jiraKey}' ({len(test_doc.jiraKey)} chars)")
                else:
                    print(f"Test {test_id}: jiraKey = None")
        
        print(f"\n{'='*60}")
        print(f"SUMMARY:")
        print(f"  Total failed tests checked: {len(failed_ids)}")
        print(f"  Tests with jiraKey > 50 chars: {len(problematic)}")
        print('='*60)
        
        conn.close()
        await migrator.close()
        
    except Exception as e:
        print(f"Error: {e}")
        await migrator.close()

if __name__ == "__main__":
    asyncio.run(check_jira_key_length())