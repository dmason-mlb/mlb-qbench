#!/usr/bin/env python3
"""Re-migrate failed tests after fixing TestDoc model.

This script specifically targets tests that failed during the initial migration
due to testType validation errors (e.g., "Automated" not being a valid type).
"""

import asyncio
import json
import sqlite3
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import structlog

logger = structlog.get_logger()


async def get_failed_test_ids(checkpoint_file: str = "migration_checkpoint.json") -> List[int]:
    """Extract test IDs that failed from checkpoint file."""
    try:
        with open(checkpoint_file, 'r') as f:
            data = json.load(f)
        
        failed_ids = []
        for error in data['stats']['errors']:
            # Parse ID from error message like "ID 991245: ..."
            if error.startswith("ID "):
                try:
                    test_id = int(error.split(":")[0].replace("ID ", ""))
                    failed_ids.append(test_id)
                except:
                    continue
        
        logger.info(f"Found {len(failed_ids)} failed test IDs to re-migrate")
        return failed_ids
    except FileNotFoundError:
        logger.error(f"Checkpoint file {checkpoint_file} not found")
        return []
    except Exception as e:
        logger.error(f"Error reading checkpoint file: {e}")
        return []


async def remigrate_failed_tests(
    failed_ids: List[int],
    sqlite_path: str = "testrail_data.db",
    postgres_dsn: str = None
):
    """Re-migrate specific test IDs that failed."""
    if not failed_ids:
        logger.info("No failed tests to re-migrate")
        return
    
    # Create migrator
    migrator = OptimizedTestRailMigrator(
        sqlite_path=sqlite_path,
        postgres_dsn=postgres_dsn,
        batch_size=100,  # Smaller batch for targeted migration
        checkpoint_interval=1000
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Connect to SQLite
        cursor = migrator.sqlite_conn.cursor()
        
        # Build query for specific IDs
        id_list = ','.join(str(id) for id in failed_ids)
        query = f"""
            SELECT 
                id, suite_id, section_id, project_id, priority_id,
                title, preconditions, steps_separated, custom_fields,
                jiras, refs, comment, is_automated, created_on, updated_on
            FROM cases
            WHERE id IN ({id_list})
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        logger.info(f"Found {len(rows)} tests to re-migrate")
        
        # Convert and insert
        success_count = 0
        fail_count = 0
        test_docs = []
        
        for row in rows:
            try:
                test_doc = migrator.convert_to_test_doc(row)
                test_docs.append(test_doc)
                
                if len(test_docs) >= 50:
                    # Insert batch
                    result = await migrator.pg_db.batch_insert_documents_optimized(
                        test_docs,
                        migrator.embedder,
                        doc_batch_size=50,
                        embedding_batch_size=100
                    )
                    success_count += result["inserted"]
                    fail_count += result["failed"]
                    test_docs = []
                    logger.info(f"Progress: {success_count} migrated, {fail_count} failed")
                    
            except Exception as e:
                fail_count += 1
                logger.error(f"Failed to re-migrate test {row['id']}: {e}")
        
        # Insert remaining
        if test_docs:
            result = await migrator.pg_db.batch_insert_documents_optimized(
                test_docs,
                migrator.embedder,
                doc_batch_size=50,
                embedding_batch_size=100
            )
            success_count += result["inserted"]
            fail_count += result["failed"]
        
        logger.info(f"Re-migration complete: {success_count} successful, {fail_count} failed")
        
    finally:
        await migrator.close()


async def main():
    """Main entry point for re-migration."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Get failed IDs from checkpoint
    failed_ids = await get_failed_test_ids()
    
    if not failed_ids:
        print("No failed tests found in checkpoint file")
        return
    
    print(f"Found {len(failed_ids)} failed tests to re-migrate")
    response = input("Proceed with re-migration? (y/N): ")
    
    if response.lower() != 'y':
        print("Re-migration cancelled")
        return
    
    # Run re-migration
    await remigrate_failed_tests(
        failed_ids,
        postgres_dsn=os.getenv("DATABASE_URL")
    )


if __name__ == "__main__":
    asyncio.run(main())