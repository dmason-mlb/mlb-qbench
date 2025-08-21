#!/usr/bin/env python3
"""Re-migrate ALL failed tests after fixing TestDoc model.

This script reads the complete list of failed test IDs and re-migrates them
with the corrected TestDoc model that now accepts "Automated" as a valid test type.
"""

import asyncio
import sqlite3
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import structlog

logger = structlog.get_logger()


async def remigrate_all_failed_tests(
    failed_ids_file: str = "all_failed_test_ids.txt",
    sqlite_path: str = "testrail_data.db",
    postgres_dsn: str = None,
    batch_size: int = 500
):
    """Re-migrate all failed test IDs."""
    
    # Read failed IDs from file
    try:
        with open(failed_ids_file, 'r') as f:
            failed_ids = [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        logger.error(f"Failed IDs file {failed_ids_file} not found")
        return
    except Exception as e:
        logger.error(f"Error reading failed IDs file: {e}")
        return
    
    logger.info(f"Found {len(failed_ids)} failed test IDs to re-migrate")
    
    if not failed_ids:
        logger.info("No failed tests to re-migrate")
        return
    
    # Create migrator
    migrator = OptimizedTestRailMigrator(
        sqlite_path=sqlite_path,
        postgres_dsn=postgres_dsn,
        batch_size=batch_size,
        checkpoint_interval=1000
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Connect to SQLite
        cursor = migrator.sqlite_conn.cursor()
        
        # Process in batches
        total_success = 0
        total_fail = 0
        
        for i in range(0, len(failed_ids), batch_size):
            batch_ids = failed_ids[i:i+batch_size]
            id_list = ','.join(str(id) for id in batch_ids)
            
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
            
            logger.info(f"Processing batch {i//batch_size + 1}: {len(rows)} tests")
            
            test_docs = []
            for row in rows:
                try:
                    test_doc = migrator.convert_to_test_doc(row)
                    test_docs.append(test_doc)
                except Exception as e:
                    total_fail += 1
                    logger.error(f"Failed to convert test {row['id']}: {e}")
            
            if test_docs:
                # Insert batch
                result = await migrator.pg_db.batch_insert_documents_optimized(
                    test_docs,
                    migrator.embedder,
                    doc_batch_size=100,
                    embedding_batch_size=100
                )
                total_success += result["inserted"]
                total_fail += result["failed"]
                logger.info(f"Batch complete: {result['inserted']} inserted, {result['failed']} failed")
        
        logger.info(f"Re-migration complete: {total_success} successful, {total_fail} failed")
        
        # Verify final counts
        conn = await migrator.pg_db.get_connection()
        try:
            total_count = await conn.fetchval('SELECT COUNT(*) FROM test_documents')
            automated_count = await conn.fetchval(
                "SELECT COUNT(*) FROM test_documents WHERE test_type = 'Automated'"
            )
            logger.info(f"Final database state: {total_count:,} total documents, {automated_count:,} automated tests")
        finally:
            await migrator.pg_db.release_connection(conn)
        
    finally:
        await migrator.close()


async def main():
    """Main entry point for re-migration."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check if failed IDs file exists
    if not Path("all_failed_test_ids.txt").exists():
        print("all_failed_test_ids.txt not found. Run extract_all_failed_ids.py first.")
        return
    
    # Count IDs
    with open("all_failed_test_ids.txt", 'r') as f:
        id_count = sum(1 for line in f if line.strip())
    
    print(f"Found {id_count} failed tests to re-migrate")
    response = input("Proceed with re-migration? (y/N): ")
    
    if response.lower() != 'y':
        print("Re-migration cancelled")
        return
    
    # Run re-migration
    await remigrate_all_failed_tests(
        postgres_dsn=os.getenv("DATABASE_URL")
    )


if __name__ == "__main__":
    asyncio.run(main())