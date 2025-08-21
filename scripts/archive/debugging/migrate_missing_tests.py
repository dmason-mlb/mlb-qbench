#!/usr/bin/env python3
"""Migrate the remaining 294 missing tests to PostgreSQL."""

import asyncio
import sqlite3
import sys
from pathlib import Path
import json
from typing import List, Dict, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import structlog

logger = structlog.get_logger()


async def migrate_missing_tests():
    """Migrate the 294 missing tests."""
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    # Read the actually missing test IDs
    with open("actually_missing_test_ids.txt", "r") as f:
        missing_ids = [int(line.strip()) for line in f if line.strip()]
    
    print(f"Migrating {len(missing_ids)} missing tests...")
    
    migrator = OptimizedTestRailMigrator(
        sqlite_path="testrail_data.db",
        postgres_dsn=os.getenv("DATABASE_URL"),
        batch_size=50,  # Small batch size for careful migration
        checkpoint_interval=1000
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Connect to SQLite
        cursor = migrator.sqlite_conn.cursor()
        
        # Process in batches
        batch_size = 50
        total_migrated = 0
        total_failed = 0
        failed_ids = []
        
        for i in range(0, len(missing_ids), batch_size):
            batch_ids = missing_ids[i:i + batch_size]
            print(f"\n{'='*60}")
            print(f"Processing batch {i//batch_size + 1}/{(len(missing_ids) + batch_size - 1)//batch_size}")
            print(f"Test IDs: {batch_ids[0]} to {batch_ids[-1]}")
            print('='*60)
            
            # Get tests from SQLite
            placeholders = ','.join(['?'] * len(batch_ids))
            query = f"""
                SELECT 
                    id, suite_id, section_id, project_id, priority_id,
                    title, preconditions, steps_separated, custom_fields,
                    jiras, refs, comment, is_automated, created_on, updated_on
                FROM cases
                WHERE id IN ({placeholders})
            """
            
            cursor.execute(query, batch_ids)
            rows = cursor.fetchall()
            
            print(f"Found {len(rows)} tests in SQLite")
            
            # Convert to TestDocs
            test_docs = []
            for row in rows:
                try:
                    test_doc = migrator.convert_to_test_doc(row)
                    test_docs.append(test_doc)
                except Exception as e:
                    print(f"  ✗ Failed to convert test {row['id']}: {e}")
                    total_failed += 1
                    failed_ids.append(row['id'])
            
            print(f"Converted {len(test_docs)} tests to TestDoc")
            
            if test_docs:
                # Insert into PostgreSQL
                try:
                    result = await migrator.pg_db.batch_insert_documents_optimized(
                        test_docs,
                        migrator.embedder,
                        doc_batch_size=len(test_docs),
                        embedding_batch_size=25
                    )
                    
                    inserted = result.get('inserted', 0)
                    failed = result.get('failed', 0)
                    
                    print(f"  Inserted: {inserted}")
                    print(f"  Failed: {failed}")
                    
                    total_migrated += inserted
                    total_failed += failed
                    
                    if failed > 0:
                        # Track which specific tests failed
                        for test_doc in test_docs[inserted:inserted+failed]:
                            failed_ids.append(int(test_doc.uid.replace('testrail_', '')))
                    
                except Exception as e:
                    print(f"  ✗ Batch insertion error: {e}")
                    total_failed += len(test_docs)
                    for test_doc in test_docs:
                        failed_ids.append(int(test_doc.uid.replace('testrail_', '')))
        
        print(f"\n{'='*60}")
        print(f"MIGRATION COMPLETE:")
        print(f"  Total tests processed: {len(missing_ids)}")
        print(f"  Successfully migrated: {total_migrated}")
        print(f"  Failed: {total_failed}")
        print('='*60)
        
        if failed_ids:
            print(f"\nFailed test IDs:")
            for test_id in failed_ids[:10]:
                print(f"  {test_id}")
            if len(failed_ids) > 10:
                print(f"  ... and {len(failed_ids) - 10} more")
            
            # Save failed IDs
            with open("final_failed_test_ids.txt", "w") as f:
                for test_id in failed_ids:
                    f.write(f"{test_id}\n")
            print(f"\nSaved {len(failed_ids)} failed IDs to final_failed_test_ids.txt")
    
    finally:
        await migrator.close()


if __name__ == "__main__":
    asyncio.run(migrate_missing_tests())