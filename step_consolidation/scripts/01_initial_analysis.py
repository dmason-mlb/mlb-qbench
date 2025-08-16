#!/usr/bin/env python3
"""
Initial analysis of TestRail database step fields.
This script performs comprehensive analysis of step field patterns and distributions.
"""

import sqlite3
import json
import os
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Ensure directories exist
LOGS_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Setup logging
log_file = LOGS_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StepFieldAnalyzer:
    """Analyzer for TestRail step fields."""
    
    def __init__(self, db_path: Path):
        """Initialize analyzer with database path."""
        self.db_path = db_path
        self.conn = None
        self.stats = {
            'total_cases': 0,
            'field_presence': Counter(),
            'field_combinations': Counter(),
            'null_steps_count': 0,
            'json_parse_errors': [],
            'sample_cases': []
        }
    
    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def get_schema_info(self):
        """Get database schema information."""
        cursor = self.conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        schema_info = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema_info[table_name] = [
                {'name': col[1], 'type': col[2], 'nullable': not col[3]}
                for col in columns
            ]
        
        return schema_info
    
    def analyze_step_fields(self, sample_size: int = 1000):
        """Analyze step field patterns and distributions."""
        cursor = self.conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM cases")
        self.stats['total_cases'] = cursor.fetchone()[0]
        logger.info(f"Total cases in database: {self.stats['total_cases']}")
        
        # Get sample of cases for analysis
        query = """
        SELECT id, steps, steps_separated, steps_combined 
        FROM cases 
        ORDER BY RANDOM() 
        LIMIT ?
        """
        cursor.execute(query, (sample_size,))
        cases = cursor.fetchall()
        
        logger.info(f"Analyzing {len(cases)} sample cases...")
        
        for case in cases:
            case_id = case['id']
            steps = case['steps']
            steps_separated = case['steps_separated']
            steps_combined = case['steps_combined']
            
            # Track field presence
            fields_present = []
            if steps and steps.strip():
                fields_present.append('steps')
                self.stats['field_presence']['steps'] += 1
            
            if steps_separated and steps_separated.strip():
                fields_present.append('steps_separated')
                self.stats['field_presence']['steps_separated'] += 1
                
                # Try to parse JSON
                try:
                    json_data = json.loads(steps_separated)
                    # Store sample for structure analysis
                    if len(self.stats['sample_cases']) < 10:
                        self.stats['sample_cases'].append({
                            'id': case_id,
                            'json_structure': json_data[:2] if isinstance(json_data, list) else json_data
                        })
                except json.JSONDecodeError as e:
                    self.stats['json_parse_errors'].append({
                        'case_id': case_id,
                        'error': str(e)
                    })
            
            if steps_combined and steps_combined.strip():
                fields_present.append('steps_combined')
                self.stats['field_presence']['steps_combined'] += 1
            
            # Track field combinations
            if fields_present:
                combination = '+'.join(sorted(fields_present))
                self.stats['field_combinations'][combination] += 1
            else:
                self.stats['field_combinations']['no_fields'] += 1
                self.stats['null_steps_count'] += 1
        
        return self.stats
    
    def analyze_content_overlap(self, limit: int = 100):
        """Analyze content overlap between fields."""
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, steps, steps_separated, steps_combined 
        FROM cases 
        WHERE (steps IS NOT NULL AND steps_separated IS NOT NULL)
           OR (steps IS NOT NULL AND steps_combined IS NOT NULL)
           OR (steps_separated IS NOT NULL AND steps_combined IS NOT NULL)
        ORDER BY RANDOM()
        LIMIT ?
        """
        cursor.execute(query, (limit,))
        cases = cursor.fetchall()
        
        overlap_stats = {
            'steps_in_combined': 0,
            'separated_in_combined': 0,
            'steps_in_separated': 0,
            'total_overlap_cases': len(cases)
        }
        
        for case in cases:
            steps = case['steps'] or ''
            steps_separated = case['steps_separated'] or ''
            steps_combined = case['steps_combined'] or ''
            
            # Normalize for comparison
            steps_norm = steps.lower().strip()
            combined_norm = steps_combined.lower().strip()
            
            # Check if steps content is in combined
            if steps_norm and combined_norm and steps_norm in combined_norm:
                overlap_stats['steps_in_combined'] += 1
            
            # Check if separated content is in combined
            if steps_separated:
                try:
                    json_data = json.loads(steps_separated)
                    if isinstance(json_data, list):
                        for item in json_data:
                            if isinstance(item, dict):
                                content = str(item.get('content', '')).lower()
                                expected = str(item.get('expected', '')).lower()
                                if content and content in combined_norm:
                                    overlap_stats['separated_in_combined'] += 1
                                    break
                except:
                    pass
        
        return overlap_stats
    
    def generate_report(self):
        """Generate analysis report."""
        report_path = REPORTS_DIR / f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("TESTRAIL STEP FIELDS ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Database: {self.db_path}\n")
            f.write(f"Total Cases: {self.stats['total_cases']:,}\n\n")
            
            f.write("FIELD PRESENCE (Sample Analysis)\n")
            f.write("-" * 40 + "\n")
            sample_size = sum(self.stats['field_combinations'].values())
            for field, count in self.stats['field_presence'].items():
                percentage = (count / sample_size * 100) if sample_size > 0 else 0
                f.write(f"{field:20} {count:6} ({percentage:.1f}%)\n")
            
            f.write("\nFIELD COMBINATIONS\n")
            f.write("-" * 40 + "\n")
            for combo, count in sorted(self.stats['field_combinations'].items(), 
                                      key=lambda x: x[1], reverse=True):
                percentage = (count / sample_size * 100) if sample_size > 0 else 0
                f.write(f"{combo:30} {count:6} ({percentage:.1f}%)\n")
            
            f.write(f"\nCases with NO step fields: {self.stats['null_steps_count']} ")
            f.write(f"({self.stats['null_steps_count'] / sample_size * 100:.1f}%)\n")
            
            if self.stats['json_parse_errors']:
                f.write(f"\nJSON Parse Errors: {len(self.stats['json_parse_errors'])}\n")
                for error in self.stats['json_parse_errors'][:5]:
                    f.write(f"  Case {error['case_id']}: {error['error'][:50]}...\n")
            
            if self.stats['sample_cases']:
                f.write("\nSAMPLE JSON STRUCTURES (steps_separated)\n")
                f.write("-" * 40 + "\n")
                for sample in self.stats['sample_cases'][:3]:
                    f.write(f"Case {sample['id']}:\n")
                    f.write(json.dumps(sample['json_structure'], indent=2)[:500] + "...\n\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path

def main():
    """Main execution function."""
    logger.info("Starting TestRail step fields analysis...")
    
    db_path = DATA_DIR / "testrail_data_working.db"
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    analyzer = StepFieldAnalyzer(db_path)
    
    try:
        analyzer.connect()
        
        # Get schema information
        schema = analyzer.get_schema_info()
        logger.info(f"Found {len(schema)} tables in database")
        
        # Check if cases table exists and has expected columns
        if 'cases' in schema:
            case_columns = [col['name'] for col in schema['cases']]
            step_columns = [col for col in case_columns if 'step' in col.lower()]
            logger.info(f"Step-related columns in cases table: {step_columns}")
        
        # Analyze step fields
        stats = analyzer.analyze_step_fields(sample_size=1000)
        
        # Analyze content overlap
        overlap = analyzer.analyze_content_overlap(limit=100)
        logger.info(f"Content overlap analysis: {overlap}")
        
        # Generate report
        report_path = analyzer.generate_report()
        
        logger.info("Analysis complete!")
        
        # Print summary to console
        print("\n" + "=" * 60)
        print("ANALYSIS SUMMARY")
        print("=" * 60)
        print(f"Total cases: {stats['total_cases']:,}")
        print(f"Sample size: 1000")
        print(f"Cases with no step fields: {stats['null_steps_count']} ({stats['null_steps_count']/10:.1f}%)")
        print(f"JSON parse errors: {len(stats['json_parse_errors'])}")
        print(f"\nReport saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise
    finally:
        analyzer.close()

if __name__ == "__main__":
    main()