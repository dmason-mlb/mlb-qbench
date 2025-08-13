#!/usr/bin/env python3
"""Analyze TestRail data structure and propose mapping to QBench schema."""

import sqlite3
import json
from collections import Counter, defaultdict
from typing import Dict, List, Any

def analyze_database():
    conn = sqlite3.connect('testrail_data.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get sample tests from iOS At Bat project
    cursor.execute("""
        SELECT c.*, 
               p.name as priority_name,
               ct.name as type_name,
               s.name as section_name
        FROM cases c
        LEFT JOIN priorities p ON c.priority_id = p.id
        LEFT JOIN case_types ct ON c.type_id = ct.id
        LEFT JOIN sections s ON c.section_id = s.id
        WHERE c.project_id = 4
        LIMIT 10
    """)
    
    sample_tests = cursor.fetchall()
    
    # Analyze field usage
    field_analysis = {
        'total_tests': 0,
        'fields': defaultdict(int),
        'custom_fields_structure': set(),
        'steps_structure': set(),
        'priority_distribution': Counter(),
        'type_distribution': Counter(),
        'has_steps_separated': 0,
        'has_preconditions': 0,
        'has_jiras': 0,
        'has_refs': 0,
    }
    
    cursor.execute("""
        SELECT c.*, p.name as priority_name, ct.name as type_name
        FROM cases c
        LEFT JOIN priorities p ON c.priority_id = p.id
        LEFT JOIN case_types ct ON c.type_id = ct.id
        WHERE c.project_id = 4
    """)
    
    for row in cursor:
        field_analysis['total_tests'] += 1
        
        # Check which fields have data
        for col in row.keys():
            if row[col] is not None and row[col] != '':
                field_analysis['fields'][col] += 1
        
        # Analyze custom fields structure
        if row['custom_fields']:
            try:
                custom = json.loads(row['custom_fields'])
                field_analysis['custom_fields_structure'].update(custom.keys())
            except:
                pass
        
        # Analyze steps structure
        if row['steps_separated']:
            field_analysis['has_steps_separated'] += 1
            try:
                steps = json.loads(row['steps_separated'])
                if steps and len(steps) > 0:
                    field_analysis['steps_structure'].update(steps[0].keys())
            except:
                pass
        
        if row['preconditions']:
            field_analysis['has_preconditions'] += 1
        
        if row['jiras']:
            field_analysis['has_jiras'] += 1
            
        if row['refs'] or row['refs_custom']:
            field_analysis['has_refs'] += 1
        
        field_analysis['priority_distribution'][row['priority_name']] += 1
        field_analysis['type_distribution'][row['type_name']] += 1
    
    # Get section hierarchy for folder structure
    cursor.execute("""
        WITH RECURSIVE section_path AS (
            SELECT id, name, parent_id, name as path
            FROM sections
            WHERE parent_id IS NULL AND suite_id IN (SELECT id FROM suites WHERE project_id = 4)
            
            UNION ALL
            
            SELECT s.id, s.name, s.parent_id, sp.path || '/' || s.name
            FROM sections s
            JOIN section_path sp ON s.parent_id = sp.id
        )
        SELECT * FROM section_path
        LIMIT 20
    """)
    
    sections = cursor.fetchall()
    
    conn.close()
    
    # Print analysis results
    print("=" * 80)
    print("TESTRAIL DATABASE ANALYSIS - iOS At Bat Project")
    print("=" * 80)
    print(f"\nTotal tests: {field_analysis['total_tests']}")
    print(f"Tests with steps_separated: {field_analysis['has_steps_separated']}")
    print(f"Tests with preconditions: {field_analysis['has_preconditions']}")
    print(f"Tests with JIRA references: {field_analysis['has_jiras']}")
    print(f"Tests with other references: {field_analysis['has_refs']}")
    
    print("\n" + "=" * 40)
    print("FIELD USAGE (% of tests with data):")
    print("=" * 40)
    for field, count in sorted(field_analysis['fields'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / field_analysis['total_tests']) * 100
        print(f"{field:30} {percentage:6.1f}% ({count} tests)")
    
    print("\n" + "=" * 40)
    print("CUSTOM FIELDS STRUCTURE:")
    print("=" * 40)
    print(list(field_analysis['custom_fields_structure']))
    
    print("\n" + "=" * 40)
    print("STEPS STRUCTURE:")
    print("=" * 40)
    print(list(field_analysis['steps_structure']))
    
    print("\n" + "=" * 40)
    print("PRIORITY DISTRIBUTION:")
    print("=" * 40)
    for priority, count in field_analysis['priority_distribution'].most_common():
        print(f"{priority:30} {count:6} tests")
    
    print("\n" + "=" * 40)
    print("TYPE DISTRIBUTION:")
    print("=" * 40)
    for test_type, count in field_analysis['type_distribution'].most_common():
        print(f"{test_type:30} {count:6} tests")
    
    print("\n" + "=" * 40)
    print("SAMPLE TESTS:")
    print("=" * 40)
    for i, test in enumerate(sample_tests[:3], 1):
        print(f"\nTest {i}:")
        print(f"  ID: {test['id']}")
        print(f"  Title: {test['title'][:80]}...")
        print(f"  Priority: {test['priority_name']}")
        print(f"  Type: {test['type_name']}")
        print(f"  Section: {test['section_name']}")
        if test['preconditions']:
            print(f"  Preconditions: {test['preconditions'][:100]}...")
        if test['steps_separated']:
            try:
                steps = json.loads(test['steps_separated'])
                print(f"  Steps: {len(steps)} steps")
                if steps:
                    print(f"    First step: {steps[0]}")
            except:
                pass
    
    print("\n" + "=" * 40)
    print("SAMPLE FOLDER STRUCTURE:")
    print("=" * 40)
    for section in sections[:10]:
        print(f"  {section['path']}")

if __name__ == "__main__":
    analyze_database()