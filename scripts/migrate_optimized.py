#!/usr/bin/env python3
"""Optimized migration script with significantly improved performance.

This version addresses the performance degradation issues found during
the initial migration attempt, implementing several key optimizations:

1. Batch embedding generation - pre-generate all embeddings upfront
2. Optimized database operations - prepared statements and batch transactions
3. Configurable checkpointing - save progress at regular intervals
4. Memory management - process data in controlled chunks
"""

import asyncio
import json
import os
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import structlog
from tqdm import tqdm

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.postgres_vector_optimized import OptimizedPostgresVectorDB
from src.embedder import get_embedder
from src.models.test_models import TestDoc, TestStep

logger = structlog.get_logger()


class OptimizedTestRailMigrator:
    """Optimized migrator with improved performance for 100k+ documents."""
    
    def __init__(
        self,
        sqlite_path: str = "testrail_data.db",
        postgres_dsn: Optional[str] = None,
        batch_size: int = 500,
        checkpoint_interval: int = 5000,
        dry_run: bool = False,
        resume_from: int = 0
    ):
        """Initialize the optimized migrator.
        
        Args:
            sqlite_path: Path to TestRail SQLite database
            postgres_dsn: PostgreSQL connection string
            batch_size: Number of records to process in each batch
            checkpoint_interval: Save progress every N records
            dry_run: If True, don't actually write to PostgreSQL
            resume_from: Test case ID to resume from (for interrupted migrations)
        """
        self.sqlite_path = sqlite_path
        self.postgres_dsn = postgres_dsn
        self.batch_size = batch_size
        self.checkpoint_interval = checkpoint_interval
        self.dry_run = dry_run
        self.resume_from = resume_from
        
        self.sqlite_conn = None
        self.pg_db = None
        self.embedder = None
        
        # Performance tracking
        self.stats = {
            "total": 0,
            "processed": 0,
            "migrated": 0,
            "failed": 0,
            "skipped": 0,
            "errors": [],
            "start_time": None,
            "checkpoints": []
        }
        
        # Cache for frequently accessed data
        self.section_cache = {}
        self.priority_cache = {}
    
    async def initialize(self):
        """Initialize database connections and embedder."""
        # Connect to SQLite
        self.sqlite_conn = sqlite3.connect(self.sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        # Pre-load caches
        self._load_caches()
        
        # Initialize PostgreSQL with optimized settings
        if not self.dry_run:
            self.pg_db = OptimizedPostgresVectorDB(self.postgres_dsn)
            await self.pg_db.initialize()
        
        # Initialize embedder
        self.embedder = get_embedder()
        
        self.stats["start_time"] = time.time()
        
        logger.info("Optimized migrator initialized",
                   sqlite_path=self.sqlite_path,
                   dry_run=self.dry_run,
                   batch_size=self.batch_size,
                   checkpoint_interval=self.checkpoint_interval)
    
    def _load_caches(self):
        """Pre-load frequently accessed data into memory."""
        cursor = self.sqlite_conn.cursor()
        
        # Load all sections
        sections = cursor.execute(
            "SELECT id, name, parent_id FROM sections"
        ).fetchall()
        
        for section in sections:
            self.section_cache[section['id']] = {
                'name': section['name'],
                'parent_id': section['parent_id']
            }
        
        # Load all priorities
        priorities = cursor.execute(
            "SELECT id, name FROM priorities"
        ).fetchall()
        
        for priority in priorities:
            self.priority_cache[priority['id']] = priority['name']
        
        logger.info(f"Loaded caches: {len(self.section_cache)} sections, {len(self.priority_cache)} priorities")
    
    async def close(self):
        """Close database connections."""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        
        if self.pg_db:
            await self.pg_db.close()
    
    def get_section_path(self, section_id: int) -> str:
        """Build the folder structure path for a section using cache."""
        path_parts = []
        current_id = section_id
        
        while current_id and current_id in self.section_cache:
            section = self.section_cache[current_id]
            path_parts.insert(0, section['name'])
            current_id = section['parent_id']
        
        return "/".join(path_parts) if path_parts else ""
    
    def get_priority_name(self, priority_id: Optional[int]) -> Optional[str]:
        """Get priority name from ID using cache."""
        if not priority_id or priority_id not in self.priority_cache:
            return None
        
        priority_name = self.priority_cache[priority_id]
        
        # Map TestRail priority format to expected enum values
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
        """Parse TestRail steps JSON into TestStep objects."""
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
            return []
    
    def convert_to_test_doc(self, row: sqlite3.Row) -> TestDoc:
        """Convert SQLite row to TestDoc model."""
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
            testCaseId=str(row['id']),
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
            source="functional_tests_xray.json",
            customFields={
                "suite_id": row['suite_id'],
                "section_id": row['section_id'],
                "project_id": row['project_id'],
                "refs": row['refs'],
                "is_automated": row['is_automated'],
                "created_on": row['created_on'],
                "updated_on": row['updated_on'],
                "original_source": "TestRail"
            }
        )
    
    async def save_checkpoint(self, last_id: int):
        """Save migration checkpoint to file."""
        checkpoint_file = "migration_checkpoint.json"
        checkpoint_data = {
            "last_id": last_id,
            "timestamp": datetime.now().isoformat(),
            "stats": self.stats
        }
        
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        logger.info(f"Checkpoint saved at ID {last_id}")
    
    async def run(self, limit: Optional[int] = None):
        """Run the optimized migration."""
        cursor = self.sqlite_conn.cursor()
        
        # Get total count
        where_clause = f"WHERE id >= {self.resume_from}" if self.resume_from else ""
        self.stats["total"] = cursor.execute(
            f"SELECT COUNT(*) FROM cases {where_clause}"
        ).fetchone()[0]
        
        if limit:
            self.stats["total"] = min(self.stats["total"], limit)
        
        logger.info(f"Starting optimized migration of {self.stats['total']} test cases")
        
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
        
        # Process in larger batches for efficiency
        with tqdm(total=self.stats["total"], desc="Migrating tests") as pbar:
            batch = []
            last_checkpoint_id = self.resume_from
            
            for row in cursor:
                batch.append(row)
                self.stats["processed"] += 1
                
                if len(batch) >= self.batch_size:
                    # Convert batch to TestDocs
                    test_docs = []
                    for r in batch:
                        try:
                            test_doc = self.convert_to_test_doc(r)
                            test_docs.append(test_doc)
                        except Exception as e:
                            self.stats["failed"] += 1
                            self.stats["errors"].append(f"ID {r['id']}: {str(e)}")
                    
                    # Insert batch
                    if test_docs and not self.dry_run:
                        result = await self.pg_db.batch_insert_documents_optimized(
                            test_docs,
                            self.embedder,
                            doc_batch_size=100,
                            embedding_batch_size=200
                        )
                        
                        self.stats["migrated"] += result["inserted"]
                        self.stats["failed"] += result["failed"]
                        if result["errors"]:
                            self.stats["errors"].extend(result["errors"])
                    
                    pbar.update(len(batch))
                    
                    # Save checkpoint if needed
                    if self.stats["processed"] - last_checkpoint_id >= self.checkpoint_interval:
                        await self.save_checkpoint(batch[-1]['id'])
                        last_checkpoint_id = batch[-1]['id']
                        self.stats["checkpoints"].append(last_checkpoint_id)
                    
                    # Log progress with performance metrics
                    if self.stats["processed"] % 1000 == 0:
                        elapsed = time.time() - self.stats["start_time"]
                        rate = self.stats["processed"] / elapsed
                        eta = (self.stats["total"] - self.stats["processed"]) / rate
                        
                        logger.info("Migration progress",
                                  processed=self.stats["processed"],
                                  migrated=self.stats["migrated"],
                                  failed=self.stats["failed"],
                                  rate=f"{rate:.1f} docs/sec",
                                  eta_minutes=f"{eta/60:.1f}")
                    
                    batch = []
            
            # Process remaining batch
            if batch:
                test_docs = []
                for r in batch:
                    try:
                        test_doc = self.convert_to_test_doc(r)
                        test_docs.append(test_doc)
                    except Exception as e:
                        self.stats["failed"] += 1
                        self.stats["errors"].append(f"ID {r['id']}: {str(e)}")
                
                if test_docs and not self.dry_run:
                    result = await self.pg_db.batch_insert_documents_optimized(
                        test_docs,
                        self.embedder,
                        doc_batch_size=100,
                        embedding_batch_size=200
                    )
                    
                    self.stats["migrated"] += result["inserted"]
                    self.stats["failed"] += result["failed"]
                
                pbar.update(len(batch))
        
        # Final statistics
        total_time = time.time() - self.stats["start_time"]
        avg_rate = self.stats["migrated"] / total_time if total_time > 0 else 0
        
        self.stats["duration_seconds"] = total_time
        self.stats["average_rate"] = avg_rate
        
        logger.info("Migration completed", **self.stats)
        
        return self.stats


async def main():
    """Main migration entry point."""
    import argparse
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Optimized TestRail to PostgreSQL migration")
    parser.add_argument("--sqlite-path", default="testrail_data.db",
                       help="Path to TestRail SQLite database")
    parser.add_argument("--postgres-dsn", 
                       default=os.getenv("DATABASE_URL", "postgresql://douglas.mason@localhost/mlb_qbench"),
                       help="PostgreSQL connection string")
    parser.add_argument("--batch-size", type=int, default=500,
                       help="Batch size for processing")
    parser.add_argument("--checkpoint-interval", type=int, default=5000,
                       help="Save checkpoint every N records")
    parser.add_argument("--limit", type=int,
                       help="Limit number of tests to migrate (for testing)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Run without actually writing to PostgreSQL")
    parser.add_argument("--resume-from", type=int, default=0,
                       help="Resume from test case ID")
    
    args = parser.parse_args()
    
    # Create migrator
    migrator = OptimizedTestRailMigrator(
        sqlite_path=args.sqlite_path,
        postgres_dsn=args.postgres_dsn,
        batch_size=args.batch_size,
        checkpoint_interval=args.checkpoint_interval,
        dry_run=args.dry_run,
        resume_from=args.resume_from
    )
    
    try:
        # Initialize connections
        await migrator.initialize()
        
        # Check database statistics before migration
        if not args.dry_run:
            stats = await migrator.pg_db.get_statistics()
            print(f"\nDatabase status before migration:")
            print(f"  Documents: {stats['total_documents']}")
            print(f"  Steps: {stats['total_steps']}")
            if stats.get('table_sizes'):
                for table in stats['table_sizes']:
                    print(f"  {table['tablename']}: {table['size']}")
        
        # Run migration
        stats = await migrator.run(limit=args.limit)
        
        # Print final statistics
        print("\n=== Migration Complete ===")
        print(f"Total processed: {stats['processed']}")
        print(f"Successfully migrated: {stats['migrated']}")
        print(f"Failed: {stats['failed']}")
        print(f"Duration: {stats['duration_seconds']:.1f} seconds")
        print(f"Average rate: {stats['average_rate']:.1f} docs/sec")
        
        if stats['errors']:
            print(f"\nFirst 10 errors:")
            for error in stats['errors'][:10]:
                print(f"  - {error}")
        
        # Check database statistics after migration
        if not args.dry_run:
            stats = await migrator.pg_db.get_statistics()
            print(f"\nDatabase status after migration:")
            print(f"  Documents: {stats['total_documents']}")
            print(f"  Steps: {stats['total_steps']}")
            if stats.get('table_sizes'):
                for table in stats['table_sizes']:
                    print(f"  {table['tablename']}: {table['size']}")
        
    finally:
        await migrator.close()


if __name__ == "__main__":
    asyncio.run(main())