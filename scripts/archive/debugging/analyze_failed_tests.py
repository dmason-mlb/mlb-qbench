#!/usr/bin/env python3
"""Analyze the failed tests to understand why they can't be migrated."""

import sqlite3
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.migrate_optimized import OptimizedTestRailMigrator
import asyncio

async def analyze_failed_tests():
    """Analyze the 50 failed tests."""
    
    # Read the failed test IDs
    with open("final_failed_test_ids.txt", "r") as f:
        failed_ids = [int(line.strip()) for line in f if line.strip()]
    
    print(f"Analyzing {len(failed_ids)} failed tests...")
    
    # Connect to SQLite
    conn = sqlite3.connect("testrail_data.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get a sample of failed tests
    sample_ids = failed_ids[:5]  # First 5 tests
    
    for test_id in sample_ids:
        print(f"\n{'='*60}")
        print(f"Test ID: {test_id}")
        print('='*60)
        
        # Get test from SQLite
        cursor.execute("""
            SELECT 
                id, suite_id, section_id, project_id, priority_id,
                title, preconditions, steps_separated, custom_fields,
                jiras, refs, comment, is_automated, created_on, updated_on
            FROM cases
            WHERE id = ?
        """, (test_id,))
        
        row = cursor.fetchone()
        
        if not row:
            print(f"Test {test_id} not found in SQLite")
            continue
        
        # Analyze field lengths
        print(f"Field lengths:")
        print(f"  title: {len(row['title']) if row['title'] else 0} chars")
        print(f"  preconditions: {len(row['preconditions']) if row['preconditions'] else 0} chars")
        print(f"  steps_separated: {len(row['steps_separated']) if row['steps_separated'] else 0} chars")
        print(f"  jiras: {len(row['jiras']) if row['jiras'] else 0} chars")
        print(f"  refs: {len(row['refs']) if row['refs'] else 0} chars")
        print(f"  comment: {len(row['comment']) if row['comment'] else 0} chars")
        
        # Check custom_fields structure
        if row['custom_fields']:
            try:
                custom = json.loads(row['custom_fields'])
                print(f"  custom_fields: {len(row['custom_fields'])} chars")
                
                # Check specific fields that might be problematic
                for key, value in custom.items():
                    if isinstance(value, str) and len(value) > 50:
                        print(f"    {key}: {len(value)} chars ('{value[:50]}...')")
                    elif isinstance(value, list):
                        # Check if it's a list of long strings
                        for item in value:
                            if isinstance(item, str) and len(item) > 50:
                                print(f"    {key}[]: {len(item)} chars ('{item[:50]}...')")
                                
            except json.JSONDecodeError:
                print(f"  custom_fields: INVALID JSON")
        
        # Try to convert to TestDoc to see exact error
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
            test_doc = migrator.convert_to_test_doc(row)
            
            # Check TestDoc field lengths
            print(f"\nTestDoc field lengths:")
            print(f"  uid: {len(test_doc.uid)} chars = '{test_doc.uid}'")
            print(f"  title: {len(test_doc.title)} chars")
            print(f"  testType: {len(test_doc.testType)} chars = '{test_doc.testType}'")
            print(f"  priority: {len(test_doc.priority) if test_doc.priority else 0} chars = '{test_doc.priority}'")
            
            # Check platforms field (varchar(50)[])
            if test_doc.platforms:
                print(f"  platforms ({len(test_doc.platforms)} items):")
                for platform in test_doc.platforms:
                    if len(platform) > 50:
                        print(f"    '{platform}' ({len(platform)} chars) *** TOO LONG FOR varchar(50) ***")
                    else:
                        print(f"    '{platform}' ({len(platform)} chars)")
            
            # Check tags field
            if test_doc.tags:
                print(f"  tags ({len(test_doc.tags)} items):")
                for tag in test_doc.tags[:5]:  # First 5 tags
                    if len(tag) > 50:
                        print(f"    '{tag}' ({len(tag)} chars) *** TOO LONG FOR varchar(50) ***")
                    else:
                        print(f"    '{tag}' ({len(tag)} chars)")
            
            await migrator.close()
            
        except Exception as e:
            print(f"\nFailed to convert to TestDoc: {e}")
    
    conn.close()

if __name__ == "__main__":
    asyncio.run(analyze_failed_tests())