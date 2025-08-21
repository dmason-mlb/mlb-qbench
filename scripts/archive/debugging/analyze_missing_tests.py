#!/usr/bin/env python3
"""Analyze the missing tests to understand why they failed to migrate."""

import sqlite3
import json
from collections import Counter

def analyze_missing_tests():
    # Read missing IDs
    with open('missing_test_ids.txt', 'r') as f:
        missing_ids = [int(line.strip()) for line in f if line.strip()]
    
    print(f"Analyzing {len(missing_ids)} missing tests...")
    
    # Connect to SQLite
    conn = sqlite3.connect('testrail_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Analyze patterns in missing tests
    id_list = ','.join(str(id) for id in missing_ids)
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
    
    print(f"Found {len(rows)} of {len(missing_ids)} missing tests in SQLite")
    
    # Analyze characteristics
    is_automated_counts = Counter()
    has_title = Counter()
    has_steps = Counter()
    priority_counts = Counter()
    suite_counts = Counter()
    
    # Look for specific issues
    issues = []
    
    for row in rows:
        # Count characteristics
        is_automated_counts[row['is_automated']] += 1
        has_title[bool(row['title'] and row['title'].strip())] += 1
        has_steps[bool(row['steps_separated'])] += 1
        priority_counts[row['priority_id']] += 1
        suite_counts[row['suite_id']] += 1
        
        # Check for potential issues
        test_issues = []
        
        # Check for empty/null title
        if not row['title'] or not row['title'].strip():
            test_issues.append("Empty title")
        
        # Check for extremely long title
        if row['title'] and len(row['title']) > 1000:
            test_issues.append(f"Very long title ({len(row['title'])} chars)")
        
        # Check for invalid characters in title
        if row['title'] and ('\x00' in row['title'] or '\xff' in row['title']):
            test_issues.append("Invalid characters in title")
        
        # Check custom_fields for issues
        if row['custom_fields']:
            try:
                custom = json.loads(row['custom_fields'])
                if isinstance(custom, dict):
                    # Check for unexpected test types
                    for field in custom.values():
                        if isinstance(field, dict) and field.get('name') == 'Test Type':
                            test_type = field.get('value')
                            if test_type and test_type not in ['Manual', 'Automated', 'API', 'Performance', 'Integration', 'Unit']:
                                test_issues.append(f"Unexpected test type: {test_type}")
            except json.JSONDecodeError:
                test_issues.append("Invalid JSON in custom_fields")
        
        if test_issues:
            issues.append({
                'id': row['id'],
                'title': row['title'][:50] if row['title'] else None,
                'issues': test_issues
            })
    
    # Print analysis
    print("\n=== CHARACTERISTICS OF MISSING TESTS ===")
    print(f"\nAutomation status:")
    for status, count in is_automated_counts.items():
        print(f"  is_automated={status}: {count}")
    
    print(f"\nHas title:")
    for has, count in has_title.items():
        print(f"  {has}: {count}")
    
    print(f"\nHas steps:")
    for has, count in has_steps.items():
        print(f"  {has}: {count}")
    
    print(f"\nTop 5 suite IDs:")
    for suite_id, count in suite_counts.most_common(5):
        print(f"  Suite {suite_id}: {count} tests")
    
    print(f"\nPriority distribution:")
    for priority, count in priority_counts.items():
        print(f"  Priority {priority}: {count}")
    
    if issues:
        print(f"\n=== SPECIFIC ISSUES FOUND ({len(issues)} tests) ===")
        for issue in issues[:10]:  # Show first 10
            print(f"\nTest {issue['id']}:")
            print(f"  Title: {issue['title']}")
            print(f"  Issues: {', '.join(issue['issues'])}")
    
    # Check if these are the automated tests that failed
    automated_missing = [id for id in missing_ids if id in [row['id'] for row in rows if row['is_automated'] == 1]]
    print(f"\n=== AUTOMATED TEST ANALYSIS ===")
    print(f"Automated tests in missing list: {len(automated_missing)}")
    if automated_missing:
        print(f"First 10 automated missing IDs: {automated_missing[:10]}")
        print(f"Last 10 automated missing IDs: {automated_missing[-10:]}")
    
    conn.close()
    
    return rows

if __name__ == "__main__":
    rows = analyze_missing_tests()