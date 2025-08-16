#!/usr/bin/env python3
"""Migration script to transfer TestRail data from SQLite to PostgreSQL with pgvector.

This script handles the migration of 104k+ test cases from the TestRail SQLite database
to PostgreSQL with vector embeddings for similarity search.

Features:
    - Batch processing with configurable batch size
    - Progress tracking and resumable migration
    - Data validation and error handling
    - Dry-run mode for testing
    - Embedding generation with rate limiting
"""

import asyncio
import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.postgres_vector import PostgresVectorDB
from src.embedder import get_embedder
from src.models.test_models import TestDoc, TestStep

logger = structlog.get_logger()


class TestRailMigrator:
    """Handles migration from TestRail SQLite to PostgreSQL."""
    
    def __init__(
        self,
        sqlite_path: str = "testrail_data.db",
        postgres_dsn: Optional[str] = None,
        batch_size: int = 100,
        dry_run: bool = False,
        resume_from: int = 0
    ):
        """Initialize the migrator.
        
        Args:
            sqlite_path: Path to TestRail SQLite database
            postgres_dsn: PostgreSQL connection string
            batch_size: Number of records to process in each batch
            dry_run: If True, don't actually write to PostgreSQL
            resume_from: Test case ID to resume from (for interrupted migrations)
        """
        self.sqlite_path = sqlite_path
        self.postgres_dsn = postgres_dsn
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.resume_from = resume_from
        
        self.sqlite_conn = None
        self.pg_db = None
        self.embedder = None
        
        # Statistics
        self.stats = {
            "total": 0,
            "processed": 0,
            "migrated": 0,
            "failed": 0,
            "skipped": 0,
            "errors": []
        }
    
    async def initialize(self):
        """Initialize database connections and embedder."""
        # Connect to SQLite
        self.sqlite_conn = sqlite3.connect(self.sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        # Initialize PostgreSQL
        if not self.dry_run:
            self.pg_db = PostgresVectorDB(self.postgres_dsn)
            await self.pg_db.initialize()
        
        # Initialize embedder
        self.embedder = get_embedder()
        
        logger.info("Migrator initialized",
                   sqlite_path=self.sqlite_path,
                   dry_run=self.dry_run,
                   batch_size=self.batch_size)
    
    async def close(self):
        """Close database connections."""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        
        if self.pg_db:
            await self.pg_db.close()
    
    def get_section_path(self, section_id: int) -> str:
        """Build the folder structure path for a section.
        
        Args:
            section_id: Section ID from TestRail
            
        Returns:
            Slash-separated folder path
        """
        cursor = self.sqlite_conn.cursor()
        path_parts = []
        
        current_id = section_id
        while current_id:
            row = cursor.execute(
                "SELECT name, parent_id FROM sections WHERE id = ?",
                (current_id,)
            ).fetchone()
            
            if row:
                path_parts.insert(0, row['name'])
                current_id = row['parent_id']
            else:
                break
        
        return "/".join(path_parts) if path_parts else ""
    
    def get_priority_name(self, priority_id: Optional[int]) -> Optional[str]:
        """Get priority name from ID.
        
        Args:
            priority_id: Priority ID from TestRail
            
        Returns:
            Priority name (Critical, High, Medium, Low) or None
        """
        if not priority_id:
            return None
            
        cursor = self.sqlite_conn.cursor()
        row = cursor.execute(
            "SELECT name FROM priorities WHERE id = ?",
            (priority_id,)
        ).fetchone()
        
        if not row:
            return None
        
        # Map TestRail priority format to expected enum values
        priority_name = row['name']
        if '1 -' in priority_name or 'Critical' in priority_name:
            return 'Critical'
        elif '2 -' in priority_name or 'High' in priority_name:
            return 'High'
        elif '3 -' in priority_name or 'Medium' in priority_name:
            return 'Medium'
        elif '4 -' in priority_name or 'Low' in priority_name:
            return 'Low'
        else:
            return 'Medium'  # Default to Medium if unknown
    
    def parse_steps(self, steps_json: Optional[str]) -> List[TestStep]:
        """Parse TestRail steps JSON into TestStep objects.
        
        Args:
            steps_json: JSON string containing steps array
            
        Returns:
            List of TestStep objects
        """
        if not steps_json:
            return []
        
        try:
            steps_data = json.loads(steps_json)
            if not isinstance(steps_data, list):
                return []
            
            test_steps = []
            for i, step in enumerate(steps_data, 1):
                if isinstance(step, dict):
                    action = step.get('content', '').strip()
                    expected = step.get('expected', '').strip()
                    
                    if action:
                        test_steps.append(TestStep(
                            index=i,
                            action=action,
                            expected=[expected] if expected else []
                        ))
            
            return test_steps
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse steps JSON", steps_json=steps_json[:100])
            return []
    
    def convert_to_test_doc(self, row: sqlite3.Row) -> TestDoc:
        """Convert SQLite row to TestDoc model.
        
        Args:
            row: SQLite row from cases table
            
        Returns:
            TestDoc object ready for PostgreSQL
        """
        # Parse custom fields for JIRA key
        jira_key = None
        tags = []
        platforms = []
        
        if row['custom_fields']:
            try:
                custom_fields = json.loads(row['custom_fields'])
                
                # Look for JIRA key in various possible fields
                jira_key = (
                    custom_fields.get('jira_key') or
                    custom_fields.get('jira_id') or
                    custom_fields.get('issue_key')
                )
                
                # Extract tags if present
                if custom_fields.get('tags'):
                    if isinstance(custom_fields['tags'], list):
                        tags = custom_fields['tags']
                    elif isinstance(custom_fields['tags'], str):
                        tags = [t.strip() for t in custom_fields['tags'].split(',')]
                
                # Extract platforms if present
                if custom_fields.get('platforms'):
                    if isinstance(custom_fields['platforms'], list):
                        platforms = custom_fields['platforms']
                    elif isinstance(custom_fields['platforms'], str):
                        platforms = [p.strip() for p in custom_fields['platforms'].split(',')]
                        
            except json.JSONDecodeError:
                pass
        
        # Also check jiras field
        if not jira_key and row['jiras']:
            jiras = row['jiras'].strip()
            if jiras:
                # Take the first JIRA key if multiple
                jira_key = jiras.split(',')[0].strip()
        
        # Build folder structure
        folder_structure = self.get_section_path(row['section_id'])
        
        # Get priority name
        priority = self.get_priority_name(row['priority_id'])
        
        # Parse steps
        steps = self.parse_steps(row['steps_separated'])
        
        # Create TestDoc
        return TestDoc(
            uid=f"testrail_{row['id']}",
            testCaseId=str(row['id']),  # Convert to string as expected by model
            jiraKey=jira_key,
            title=row['title'],
            description=row['preconditions'],
            summary=row['comment'],
            steps=steps,
            priority=priority,
            tags=tags,
            platforms=platforms,
            folderStructure=folder_structure,
            testType="Manual" if not row['is_automated'] else "Automated",
            source="functional_tests_xray.json",  # Use allowed source value
            customFields={
                "suite_id": row['suite_id'],
                "section_id": row['section_id'],
                "project_id": row['project_id'],
                "refs": row['refs'],
                "is_automated": row['is_automated'],
                "created_on": row['created_on'],
                "updated_on": row['updated_on'],
                "original_source": "TestRail"  # Keep track of actual source
            }
        )
    
    async def migrate_batch(self, rows: List[sqlite3.Row]) -> Dict[str, Any]:
        """Migrate a batch of test cases.
        
        Args:
            rows: Batch of SQLite rows to migrate
            
        Returns:
            Migration statistics for the batch
        """
        test_docs = []
        
        for row in rows:
            try:
                test_doc = self.convert_to_test_doc(row)
                test_docs.append(test_doc)
            except Exception as e:
                logger.error("Failed to convert row", 
                           test_id=row['id'],
                           error=str(e))
                self.stats["failed"] += 1
                self.stats["errors"].append(f"ID {row['id']}: {str(e)}")
                continue
        
        if test_docs and not self.dry_run:
            # Insert into PostgreSQL with embeddings
            result = await self.pg_db.batch_insert_documents(
                test_docs, 
                self.embedder,
                batch_size=25  # Smaller batch for embedding API
            )
            
            self.stats["migrated"] += result["inserted"]
            self.stats["failed"] += result["failed"]
            
            if result["errors"]:
                self.stats["errors"].extend(result["errors"])
            
            return result
        else:
            # Dry run - just count
            self.stats["migrated"] += len(test_docs)
            return {"inserted": len(test_docs), "failed": 0}
    
    async def run(self, limit: Optional[int] = None):
        """Run the migration.
        
        Args:
            limit: Optional limit on number of tests to migrate (for testing)
        """
        cursor = self.sqlite_conn.cursor()
        
        # Get total count
        where_clause = f"WHERE id >= {self.resume_from}" if self.resume_from else ""
        self.stats["total"] = cursor.execute(
            f"SELECT COUNT(*) FROM cases {where_clause}"
        ).fetchone()[0]
        
        if limit:
            self.stats["total"] = min(self.stats["total"], limit)
        
        logger.info(f"Starting migration of {self.stats['total']} test cases")
        
        # Query for test cases
        query = f"""
            SELECT 
                id, suite_id, section_id, project_id, priority_id,
                title, preconditions, steps_separated, custom_fields,
                jiras, refs, comment, is_automated, created_on, updated_on
            FROM cases
            {where_clause}
            ORDER BY id
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        
        # Process in batches with progress bar
        with tqdm(total=self.stats["total"], desc="Migrating tests") as pbar:
            batch = []
            
            for row in cursor:
                batch.append(row)
                self.stats["processed"] += 1
                
                if len(batch) >= self.batch_size:
                    await self.migrate_batch(batch)
                    pbar.update(len(batch))
                    batch = []
                    
                    # Log progress periodically
                    if self.stats["processed"] % 1000 == 0:
                        logger.info("Migration progress",
                                  processed=self.stats["processed"],
                                  migrated=self.stats["migrated"],
                                  failed=self.stats["failed"])
            
            # Process remaining batch
            if batch:
                await self.migrate_batch(batch)
                pbar.update(len(batch))
        
        # Final statistics
        logger.info("Migration completed", **self.stats)
        
        return self.stats


async def main():
    """Main migration entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate TestRail data to PostgreSQL")
    parser.add_argument("--sqlite-path", default="testrail_data.db",
                       help="Path to TestRail SQLite database")
    parser.add_argument("--postgres-dsn", 
                       default=os.getenv("DATABASE_URL", "postgresql://postgres@localhost/mlb_qbench"),
                       help="PostgreSQL connection string")
    parser.add_argument("--batch-size", type=int, default=100,
                       help="Batch size for processing")
    parser.add_argument("--limit", type=int,
                       help="Limit number of tests to migrate (for testing)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run without actually writing to PostgreSQL")
    parser.add_argument("--resume-from", type=int, default=0,
                       help="Resume from test case ID")
    
    args = parser.parse_args()
    
    # Create migrator
    migrator = TestRailMigrator(
        sqlite_path=args.sqlite_path,
        postgres_dsn=args.postgres_dsn,
        batch_size=args.batch_size,
        dry_run=args.dry_run,
        resume_from=args.resume_from
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Run migration
        stats = await migrator.run(limit=args.limit)
        
        # Print final statistics
        print("\n=== Migration Complete ===")
        print(f"Total processed: {stats['processed']}")
        print(f"Successfully migrated: {stats['migrated']}")
        print(f"Failed: {stats['failed']}")
        print(f"Skipped: {stats['skipped']}")
        
        if stats['errors']:
            print(f"\nFirst 10 errors:")
            for error in stats['errors'][:10]:
                print(f"  - {error}")
        
    finally:
        await migrator.close()


if __name__ == "__main__":
    asyncio.run(main())