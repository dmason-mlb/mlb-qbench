#!/usr/bin/env python3
"""Migrate the final 50 tests with jiraKey truncation."""

import asyncio
import sqlite3
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import structlog

logger = structlog.get_logger()


async def migrate_final_tests():
    """Migrate the final 50 tests with jiraKey field handling."""
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Read the failed test IDs
    with open("final_failed_test_ids.txt", "r") as f:
        failed_ids = [int(line.strip()) for line in f if line.strip()]
    
    print(f"Migrating {len(failed_ids)} final tests with jiraKey truncation...")
    
    migrator = OptimizedTestRailMigrator(
        sqlite_path="testrail_data.db",
        postgres_dsn=os.getenv("DATABASE_URL"),
        batch_size=1,  # Process one at a time to handle errors gracefully
        checkpoint_interval=1000
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Connect to SQLite
        cursor = migrator.sqlite_conn.cursor()
        
        total_migrated = 0
        total_failed = 0
        still_failed_ids = []
        
        for test_id in failed_ids:
            print(f"\nProcessing test {test_id}...")
            
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
                print(f"  Test {test_id} not found in SQLite")
                total_failed += 1
                still_failed_ids.append(test_id)
                continue
            
            try:
                # Convert to TestDoc
                test_doc = migrator.convert_to_test_doc(row)
                
                # Truncate jiraKey if it's too long
                if test_doc.jiraKey and len(test_doc.jiraKey) > 50:
                    original = test_doc.jiraKey
                    # Take the first JIRA key if there are multiple
                    if '\n' in test_doc.jiraKey:
                        first_key = test_doc.jiraKey.split('\n')[0].strip()
                        test_doc.jiraKey = first_key[:50] if len(first_key) > 50 else first_key
                    else:
                        test_doc.jiraKey = test_doc.jiraKey[:50]
                    print(f"  Truncated jiraKey from {len(original)} to {len(test_doc.jiraKey)} chars")
                
                # Insert into PostgreSQL
                result = await migrator.pg_db.batch_insert_documents_optimized(
                    [test_doc],
                    migrator.embedder,
                    doc_batch_size=1,
                    embedding_batch_size=1
                )
                
                if result.get('inserted', 0) > 0:
                    print(f"  ✓ Successfully migrated test {test_id}")
                    total_migrated += 1
                else:
                    print(f"  ✗ Failed to insert test {test_id}")
                    total_failed += 1
                    still_failed_ids.append(test_id)
                    
            except Exception as e:
                print(f"  ✗ Error processing test {test_id}: {e}")
                total_failed += 1
                still_failed_ids.append(test_id)
        
        print(f"\n{'='*60}")
        print(f"FINAL MIGRATION COMPLETE:")
        print(f"  Total tests processed: {len(failed_ids)}")
        print(f"  Successfully migrated: {total_migrated}")
        print(f"  Failed: {total_failed}")
        print('='*60)
        
        if still_failed_ids:
            print(f"\nStill failed test IDs:")
            for test_id in still_failed_ids:
                print(f"  {test_id}")
            
            # Save still failed IDs
            with open("still_failed_test_ids.txt", "w") as f:
                for test_id in still_failed_ids:
                    f.write(f"{test_id}\n")
            print(f"\nSaved {len(still_failed_ids)} still failed IDs to still_failed_test_ids.txt")
    
    finally:
        await migrator.close()


if __name__ == "__main__":
    asyncio.run(migrate_final_tests())