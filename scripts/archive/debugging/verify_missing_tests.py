#!/usr/bin/env python3
"""Verify if the 'missing' tests are actually already in PostgreSQL."""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from pathlib import Path

async def verify_missing_tests():
    """Check if the missing tests are actually in PostgreSQL."""
    load_dotenv()
    
    # Read the missing test IDs
    with open("missing_test_ids.txt", "r") as f:
        missing_ids = [int(line.strip()) for line in f if line.strip()]
    
    print(f"Checking {len(missing_ids)} supposedly missing test IDs...")
    
    # Connect to PostgreSQL
    pg_conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    
    try:
        # Check each test ID
        actually_missing = []
        actually_present = []
        
        for test_id in missing_ids:
            # Check by test_case_id
            row = await pg_conn.fetchrow(
                'SELECT uid, title FROM test_documents WHERE test_case_id = $1',
                test_id
            )
            
            if row:
                actually_present.append(test_id)
                print(f"✓ Test {test_id} IS in PostgreSQL as {row['uid']}")
            else:
                # Also check by uid pattern
                row = await pg_conn.fetchrow(
                    'SELECT uid, title FROM test_documents WHERE uid = $1',
                    f'testrail_{test_id}'
                )
                
                if row:
                    actually_present.append(test_id)
                    print(f"✓ Test {test_id} IS in PostgreSQL as {row['uid']}")
                else:
                    actually_missing.append(test_id)
                    print(f"✗ Test {test_id} NOT in PostgreSQL")
        
        print(f"\n{'='*60}")
        print(f"SUMMARY:")
        print(f"  Tests checked: {len(missing_ids)}")
        print(f"  Actually present: {len(actually_present)}")
        print(f"  Actually missing: {len(actually_missing)}")
        print('='*60)
        
        if actually_missing:
            print(f"\nActually missing test IDs:")
            for test_id in actually_missing[:10]:  # Show first 10
                print(f"  {test_id}")
            if len(actually_missing) > 10:
                print(f"  ... and {len(actually_missing) - 10} more")
        
        # Save actually missing IDs
        if actually_missing:
            with open("actually_missing_test_ids.txt", "w") as f:
                for test_id in actually_missing:
                    f.write(f"{test_id}\n")
            print(f"\nSaved {len(actually_missing)} actually missing IDs to actually_missing_test_ids.txt")
        
    finally:
        await pg_conn.close()

if __name__ == "__main__":
    asyncio.run(verify_missing_tests())