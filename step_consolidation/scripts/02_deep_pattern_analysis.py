#!/usr/bin/env python3
"""
Deep pattern analysis of step fields with focus on JSON structures and content patterns.
"""

import sqlite3
import json
import re
import os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime
from html.parser import HTMLParser

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Setup logging
log_file = LOGS_DIR / f"deep_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HTMLStripper(HTMLParser):
    """Strip HTML tags from text."""
    
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ' '.join(self.text)

def strip_html(html_text: str) -> str:
    """Remove HTML tags from text."""
    if not html_text:
        return ''
    stripper = HTMLStripper()
    stripper.feed(html_text)
    return stripper.get_text()

class DeepPatternAnalyzer:
    """Deep analysis of step field patterns and structures."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.patterns = {
            'json_structures': Counter(),
            'content_patterns': Counter(),
            'given_when_then': defaultdict(list),
            'field_lengths': defaultdict(list),
            'edge_cases': [],
            'malformed_json': [],
            'html_content': [],
            'empty_but_not_null': []
        }
    
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def analyze_json_structures(self, limit: int = 500):
        """Analyze JSON structures in steps_separated field."""
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, steps_separated 
        FROM cases 
        WHERE steps_separated IS NOT NULL AND steps_separated != ''
        ORDER BY RANDOM()
        LIMIT ?
        """
        cursor.execute(query, (limit,))
        cases = cursor.fetchall()
        
        logger.info(f"Analyzing JSON structures in {len(cases)} cases...")
        
        for case in cases:
            case_id = case['id']
            json_text = case['steps_separated']
            
            try:
                data = json.loads(json_text)
                
                # Analyze structure
                if isinstance(data, list):
                    self.patterns['json_structures']['array'] += 1
                    
                    if data:  # Non-empty array
                        first_item = data[0]
                        if isinstance(first_item, dict):
                            keys = tuple(sorted(first_item.keys()))
                            self.patterns['json_structures'][f'keys:{keys}'] += 1
                            
                            # Check for standard structure
                            if 'content' in first_item and 'expected' in first_item:
                                self.patterns['json_structures']['standard_structure'] += 1
                            else:
                                self.patterns['json_structures']['non_standard_structure'] += 1
                                
                        # Track array lengths
                        self.patterns['field_lengths']['json_array_length'].append(len(data))
                    else:
                        self.patterns['empty_but_not_null'].append({
                            'case_id': case_id,
                            'field': 'steps_separated',
                            'value': '[]'
                        })
                        
                elif isinstance(data, dict):
                    self.patterns['json_structures']['object'] += 1
                    keys = tuple(sorted(data.keys()))
                    self.patterns['json_structures'][f'object_keys:{keys}'] += 1
                else:
                    self.patterns['json_structures']['other'] += 1
                    
            except json.JSONDecodeError as e:
                self.patterns['malformed_json'].append({
                    'case_id': case_id,
                    'error': str(e),
                    'sample': json_text[:100]
                })
        
        return self.patterns['json_structures']
    
    def analyze_content_patterns(self, limit: int = 500):
        """Analyze content patterns in all step fields."""
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, steps, steps_separated, steps_combined 
        FROM cases 
        WHERE steps IS NOT NULL 
           OR steps_separated IS NOT NULL 
           OR steps_combined IS NOT NULL
        ORDER BY RANDOM()
        LIMIT ?
        """
        cursor.execute(query, (limit,))
        cases = cursor.fetchall()
        
        logger.info(f"Analyzing content patterns in {len(cases)} cases...")
        
        # Pattern regexes
        given_pattern = re.compile(r'\bGIVEN\b', re.IGNORECASE)
        when_pattern = re.compile(r'\bWHEN\b', re.IGNORECASE)
        then_pattern = re.compile(r'\bTHEN\b', re.IGNORECASE)
        and_pattern = re.compile(r'\bAND\b', re.IGNORECASE)
        
        for case in cases:
            case_id = case['id']
            
            # Analyze steps field
            if case['steps']:
                text = strip_html(case['steps'])
                if text.strip():
                    self.patterns['field_lengths']['steps'].append(len(text))
                    
                    if given_pattern.search(text):
                        self.patterns['given_when_then']['steps_given'].append(case_id)
                    if when_pattern.search(text):
                        self.patterns['given_when_then']['steps_when'].append(case_id)
                    if then_pattern.search(text):
                        self.patterns['given_when_then']['steps_then'].append(case_id)
                    
                    # Check for HTML content
                    if '<' in case['steps'] and '>' in case['steps']:
                        self.patterns['html_content'].append({
                            'case_id': case_id,
                            'field': 'steps'
                        })
                else:
                    self.patterns['empty_but_not_null'].append({
                        'case_id': case_id,
                        'field': 'steps',
                        'value': 'whitespace_only'
                    })
            
            # Analyze steps_combined field
            if case['steps_combined']:
                text = strip_html(case['steps_combined'])
                if text.strip():
                    self.patterns['field_lengths']['steps_combined'].append(len(text))
                    
                    if given_pattern.search(text):
                        self.patterns['given_when_then']['combined_given'].append(case_id)
                    if when_pattern.search(text):
                        self.patterns['given_when_then']['combined_when'].append(case_id)
                    if then_pattern.search(text):
                        self.patterns['given_when_then']['combined_then'].append(case_id)
                    
                    # Check for HTML content
                    if '<' in case['steps_combined'] and '>' in case['steps_combined']:
                        self.patterns['html_content'].append({
                            'case_id': case_id,
                            'field': 'steps_combined'
                        })
                else:
                    self.patterns['empty_but_not_null'].append({
                        'case_id': case_id,
                        'field': 'steps_combined',
                        'value': 'whitespace_only'
                    })
            
            # Analyze steps_separated JSON content
            if case['steps_separated']:
                try:
                    data = json.loads(case['steps_separated'])
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                content = item.get('content', '')
                                expected = item.get('expected', '')
                                
                                # Check patterns in content
                                if when_pattern.search(content):
                                    self.patterns['given_when_then']['separated_when'].append(case_id)
                                if given_pattern.search(content):
                                    self.patterns['given_when_then']['separated_given'].append(case_id)
                                
                                # Check patterns in expected
                                if then_pattern.search(expected):
                                    self.patterns['given_when_then']['separated_then'].append(case_id)
                except:
                    pass
        
        return self.patterns['given_when_then']
    
    def find_edge_cases(self, limit: int = 100):
        """Find edge cases and anomalies."""
        cursor = self.conn.cursor()
        
        # Find cases with very long fields
        query = """
        SELECT id, 
               LENGTH(steps) as steps_len,
               LENGTH(steps_separated) as separated_len,
               LENGTH(steps_combined) as combined_len
        FROM cases
        WHERE LENGTH(steps) > 5000 
           OR LENGTH(steps_separated) > 10000
           OR LENGTH(steps_combined) > 5000
        LIMIT ?
        """
        cursor.execute(query, (limit,))
        long_cases = cursor.fetchall()
        
        for case in long_cases:
            self.patterns['edge_cases'].append({
                'case_id': case['id'],
                'type': 'very_long_content',
                'steps_len': case['steps_len'],
                'separated_len': case['separated_len'],
                'combined_len': case['combined_len']
            })
        
        # Find cases with unusual characters
        query = """
        SELECT id, steps, steps_separated, steps_combined
        FROM cases
        WHERE steps LIKE '%�%' 
           OR steps_separated LIKE '%�%'
           OR steps_combined LIKE '%�%'
        LIMIT ?
        """
        cursor.execute(query, (limit,))
        encoding_issues = cursor.fetchall()
        
        for case in encoding_issues:
            self.patterns['edge_cases'].append({
                'case_id': case['id'],
                'type': 'encoding_issues'
            })
        
        logger.info(f"Found {len(self.patterns['edge_cases'])} edge cases")
    
    def generate_detailed_report(self):
        """Generate detailed analysis report."""
        report_path = REPORTS_DIR / f"deep_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DEEP PATTERN ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            # JSON Structure Analysis
            f.write("JSON STRUCTURE PATTERNS (steps_separated)\n")
            f.write("-" * 40 + "\n")
            for pattern, count in sorted(self.patterns['json_structures'].items(), 
                                        key=lambda x: x[1], reverse=True)[:20]:
                f.write(f"{str(pattern)[:50]:50} {count:6}\n")
            
            # Field Length Statistics
            f.write("\nFIELD LENGTH STATISTICS\n")
            f.write("-" * 40 + "\n")
            for field, lengths in self.patterns['field_lengths'].items():
                if lengths:
                    avg_len = sum(lengths) / len(lengths)
                    max_len = max(lengths)
                    min_len = min(lengths)
                    f.write(f"{field:20} Avg: {avg_len:8.0f} Max: {max_len:8} Min: {min_len:8}\n")
            
            # GIVEN/WHEN/THEN Pattern Distribution
            f.write("\nGIVEN/WHEN/THEN PATTERN DISTRIBUTION\n")
            f.write("-" * 40 + "\n")
            for pattern, case_ids in self.patterns['given_when_then'].items():
                f.write(f"{pattern:25} {len(case_ids):6} cases\n")
            
            # Edge Cases
            if self.patterns['edge_cases']:
                f.write("\nEDGE CASES\n")
                f.write("-" * 40 + "\n")
                edge_case_types = Counter(e['type'] for e in self.patterns['edge_cases'])
                for case_type, count in edge_case_types.items():
                    f.write(f"{case_type:30} {count:6}\n")
            
            # Malformed JSON
            if self.patterns['malformed_json']:
                f.write(f"\nMALFORMED JSON: {len(self.patterns['malformed_json'])} cases\n")
                f.write("-" * 40 + "\n")
                for error in self.patterns['malformed_json'][:5]:
                    f.write(f"Case {error['case_id']}: {error['error'][:50]}\n")
            
            # HTML Content
            if self.patterns['html_content']:
                f.write(f"\nHTML CONTENT FOUND: {len(self.patterns['html_content'])} cases\n")
                html_by_field = Counter(h['field'] for h in self.patterns['html_content'])
                for field, count in html_by_field.items():
                    f.write(f"  {field:20} {count:6}\n")
            
            # Empty but not null
            if self.patterns['empty_but_not_null']:
                f.write(f"\nEMPTY BUT NOT NULL: {len(self.patterns['empty_but_not_null'])} cases\n")
                empty_by_field = Counter(e['field'] for e in self.patterns['empty_but_not_null'])
                for field, count in empty_by_field.items():
                    f.write(f"  {field:20} {count:6}\n")
        
        logger.info(f"Detailed report generated: {report_path}")
        return report_path

def main():
    """Main execution function."""
    logger.info("Starting deep pattern analysis...")
    
    db_path = DATA_DIR / "testrail_data_working.db"
    analyzer = DeepPatternAnalyzer(db_path)
    
    try:
        analyzer.connect()
        
        # Analyze JSON structures
        json_stats = analyzer.analyze_json_structures(limit=500)
        logger.info(f"JSON structure analysis complete")
        
        # Analyze content patterns
        pattern_stats = analyzer.analyze_content_patterns(limit=500)
        logger.info(f"Content pattern analysis complete")
        
        # Find edge cases
        analyzer.find_edge_cases(limit=100)
        
        # Generate report
        report_path = analyzer.generate_detailed_report()
        
        print("\n" + "=" * 60)
        print("DEEP ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Malformed JSON cases: {len(analyzer.patterns['malformed_json'])}")
        print(f"HTML content cases: {len(analyzer.patterns['html_content'])}")
        print(f"Edge cases found: {len(analyzer.patterns['edge_cases'])}")
        print(f"Empty but not null: {len(analyzer.patterns['empty_but_not_null'])}")
        print(f"\nReport saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Deep analysis failed: {e}", exc_info=True)
        raise
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()