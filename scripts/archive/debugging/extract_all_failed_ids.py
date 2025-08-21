#!/usr/bin/env python3
"""Extract all failed test IDs from the migration log."""

import re

def extract_failed_ids_from_log(log_file: str = "migration.log") -> list[int]:
    """Extract all unique test IDs that failed from the migration log."""
    all_ids = set()
    
    with open(log_file, 'r') as f:
        for line in f:
            if 'Migration completed' in line and 'errors=' in line:
                # Extract all IDs from the errors array
                ids = re.findall(r'ID (\d+):', line)
                all_ids.update(int(id) for id in ids)
                break
    
    return sorted(list(all_ids))

if __name__ == "__main__":
    failed_ids = extract_failed_ids_from_log()
    
    print(f"Found {len(failed_ids)} unique failed test IDs")
    print(f"First 10: {failed_ids[:10]}")
    print(f"Last 10: {failed_ids[-10:]}")
    
    # Write to file
    with open('all_failed_test_ids.txt', 'w') as f:
        for test_id in failed_ids:
            f.write(f"{test_id}\n")
    
    print(f"\nWrote all {len(failed_ids)} IDs to all_failed_test_ids.txt")