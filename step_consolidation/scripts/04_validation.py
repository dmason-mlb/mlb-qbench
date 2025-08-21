#!/usr/bin/env python3
"""
Validation script to verify consolidation results.
Checks data integrity, completeness, and quality of consolidated fields.
"""

import sqlite3
import json
import random
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime
from collections import Counter

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"

# Setup logging
log_file = LOGS_DIR / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ConsolidationValidator:
    """Validates the consolidation results."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self.validation_results = {
            'total_cases': 0,
            'consolidated_cases': 0,
            'null_consolidated': 0,
            'data_preserved': 0,
            'data_loss': 0,
            'structure_valid': 0,
            'structure_invalid': 0,
            'sample_validations': [],
            'issues': []
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
    
    def validate_statistics(self):
        """Validate basic statistics of consolidation."""
        cursor = self.conn.cursor()
        
        # Total cases
        cursor.execute("SELECT COUNT(*) FROM cases")
        self.validation_results['total_cases'] = cursor.fetchone()[0]
        
        # Cases with consolidated_steps
        cursor.execute("SELECT COUNT(*) FROM cases WHERE consolidated_steps IS NOT NULL")
        self.validation_results['consolidated_cases'] = cursor.fetchone()[0]
        
        # Cases with null consolidated_steps
        cursor.execute("SELECT COUNT(*) FROM cases WHERE consolidated_steps IS NULL")
        self.validation_results['null_consolidated'] = cursor.fetchone()[0]
        
        # Cases that had original steps but no consolidated
        cursor.execute("""
        SELECT COUNT(*) FROM cases 
        WHERE consolidated_steps IS NULL 
        AND (steps IS NOT NULL OR steps_separated IS NOT NULL OR steps_combined IS NOT NULL)
        """)
        potentially_missing = cursor.fetchone()[0]
        
        if potentially_missing > 0:
            self.validation_results['issues'].append({
                'type': 'potential_data_loss',
                'count': potentially_missing,
                'description': 'Cases with original steps but no consolidated output'
            })
        
        logger.info(f"Statistics validated: {self.validation_results['total_cases']} total, "
                   f"{self.validation_results['consolidated_cases']} consolidated")
    
    def validate_structure(self, sample_size: int = 100):
        """Validate the structure of consolidated JSON."""
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, consolidated_steps 
        FROM cases 
        WHERE consolidated_steps IS NOT NULL
        ORDER BY RANDOM()
        LIMIT ?
        """
        cursor.execute(query, (sample_size,))
        cases = cursor.fetchall()
        
        for case in cases:
            case_id = case['id']
            consolidated_json = case['consolidated_steps']
            
            try:
                data = json.loads(consolidated_json)
                
                # Check required structure
                required_keys = ['preconditions', 'steps', 'expected_results', 'metadata']
                if all(key in data for key in required_keys):
                    self.validation_results['structure_valid'] += 1
                    
                    # Check metadata
                    if 'source_fields' in data['metadata']:
                        if not data['metadata']['source_fields']:
                            self.validation_results['issues'].append({
                                'type': 'empty_source_fields',
                                'case_id': case_id
                            })
                else:
                    self.validation_results['structure_invalid'] += 1
                    self.validation_results['issues'].append({
                        'type': 'missing_required_keys',
                        'case_id': case_id,
                        'missing': [k for k in required_keys if k not in data]
                    })
                    
            except json.JSONDecodeError as e:
                self.validation_results['structure_invalid'] += 1
                self.validation_results['issues'].append({
                    'type': 'invalid_json',
                    'case_id': case_id,
                    'error': str(e)
                })
    
    def validate_data_preservation(self, sample_size: int = 50):
        """Validate that original data is preserved in consolidation."""
        cursor = self.conn.cursor()
        
        query = """
        SELECT id, steps, steps_separated, steps_combined, consolidated_steps
        FROM cases
        WHERE consolidated_steps IS NOT NULL
        AND (steps IS NOT NULL OR steps_separated IS NOT NULL OR steps_combined IS NOT NULL)
        ORDER BY RANDOM()
        LIMIT ?
        """
        cursor.execute(query, (sample_size,))
        cases = cursor.fetchall()
        
        for case in cases:
            case_id = case['id']
            validation = {
                'case_id': case_id,
                'original_fields': [],
                'preserved': True,
                'details': []
            }
            
            # Count original content
            original_char_count = 0
            if case['steps']:
                original_char_count += len(case['steps'])
                validation['original_fields'].append('steps')
            if case['steps_separated']:
                original_char_count += len(case['steps_separated'])
                validation['original_fields'].append('steps_separated')
            if case['steps_combined']:
                original_char_count += len(case['steps_combined'])
                validation['original_fields'].append('steps_combined')
            
            # Parse consolidated
            try:
                consolidated = json.loads(case['consolidated_steps'])
                
                # Check if source fields match
                if set(validation['original_fields']) != set(consolidated['metadata']['source_fields']):
                    validation['preserved'] = False
                    validation['details'].append('Source fields mismatch')
                
                # Check content presence
                consolidated_text = ' '.join(
                    consolidated['preconditions'] + 
                    consolidated['steps'] + 
                    consolidated['expected_results']
                )
                
                # For steps_separated, check if JSON was parsed
                if case['steps_separated']:
                    try:
                        json_data = json.loads(case['steps_separated'])
                        if isinstance(json_data, list) and json_data:
                            # Check if content was extracted
                            if not any([consolidated['steps'], consolidated['expected_results']]):
                                validation['preserved'] = False
                                validation['details'].append('JSON content not extracted')
                    except:
                        pass
                
                # Basic length check (consolidated should generally be similar or longer)
                if len(consolidated_text) < original_char_count * 0.5:
                    validation['details'].append(f'Possible content loss: {len(consolidated_text)} vs {original_char_count} chars')
                
            except Exception as e:
                validation['preserved'] = False
                validation['details'].append(f'Error: {str(e)}')
            
            self.validation_results['sample_validations'].append(validation)
            
            if validation['preserved']:
                self.validation_results['data_preserved'] += 1
            else:
                self.validation_results['data_loss'] += 1
    
    def generate_validation_report(self):
        """Generate validation report."""
        report_path = REPORTS_DIR / f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("CONSOLIDATION VALIDATION REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            # Statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Cases:          {self.validation_results['total_cases']:,}\n")
            f.write(f"Consolidated:         {self.validation_results['consolidated_cases']:,}\n")
            f.write(f"Null Consolidated:    {self.validation_results['null_consolidated']:,}\n")
            
            consolidation_rate = (self.validation_results['consolidated_cases'] / 
                                self.validation_results['total_cases'] * 100)
            f.write(f"Consolidation Rate:   {consolidation_rate:.2f}%\n\n")
            
            # Structure Validation
            f.write("STRUCTURE VALIDATION\n")
            f.write("-" * 40 + "\n")
            f.write(f"Valid Structure:      {self.validation_results['structure_valid']}\n")
            f.write(f"Invalid Structure:    {self.validation_results['structure_invalid']}\n\n")
            
            # Data Preservation
            f.write("DATA PRESERVATION (Sample)\n")
            f.write("-" * 40 + "\n")
            f.write(f"Data Preserved:       {self.validation_results['data_preserved']}\n")
            f.write(f"Potential Data Loss:  {self.validation_results['data_loss']}\n\n")
            
            # Issues
            if self.validation_results['issues']:
                f.write("ISSUES FOUND\n")
                f.write("-" * 40 + "\n")
                
                issue_types = Counter(issue['type'] for issue in self.validation_results['issues'])
                for issue_type, count in issue_types.most_common():
                    f.write(f"{issue_type:30} {count:6}\n")
                
                # Sample issues
                f.write("\nSample Issues:\n")
                for issue in self.validation_results['issues'][:10]:
                    f.write(f"  {issue}\n")
            
            # Sample Validations
            f.write("\nSAMPLE VALIDATION DETAILS\n")
            f.write("-" * 40 + "\n")
            for validation in self.validation_results['sample_validations'][:5]:
                f.write(f"Case {validation['case_id']}:\n")
                f.write(f"  Original fields: {', '.join(validation['original_fields'])}\n")
                f.write(f"  Preserved: {validation['preserved']}\n")
                if validation['details']:
                    f.write(f"  Details: {'; '.join(validation['details'])}\n")
                f.write("\n")
        
        logger.info(f"Validation report generated: {report_path}")
        return report_path
    
    def spot_check_cases(self, case_ids: List[int] = None):
        """Perform spot checks on specific cases."""
        cursor = self.conn.cursor()
        
        if not case_ids:
            # Get random sample
            cursor.execute("""
            SELECT id FROM cases 
            WHERE consolidated_steps IS NOT NULL
            ORDER BY RANDOM() LIMIT 5
            """)
            case_ids = [row[0] for row in cursor.fetchall()]
        
        spot_checks = []
        for case_id in case_ids:
            cursor.execute("""
            SELECT id, steps, steps_separated, steps_combined, consolidated_steps
            FROM cases WHERE id = ?
            """, (case_id,))
            case = cursor.fetchone()
            
            if case:
                check = {
                    'case_id': case_id,
                    'has_steps': bool(case['steps']),
                    'has_separated': bool(case['steps_separated']),
                    'has_combined': bool(case['steps_combined']),
                    'has_consolidated': bool(case['consolidated_steps'])
                }
                
                if case['consolidated_steps']:
                    try:
                        data = json.loads(case['consolidated_steps'])
                        check['consolidated_structure'] = {
                            'preconditions_count': len(data.get('preconditions', [])),
                            'steps_count': len(data.get('steps', [])),
                            'expected_results_count': len(data.get('expected_results', [])),
                            'source_fields': data.get('metadata', {}).get('source_fields', [])
                        }
                    except:
                        check['consolidated_structure'] = 'Invalid JSON'
                
                spot_checks.append(check)
        
        return spot_checks

def main():
    """Main execution function."""
    logger.info("Starting consolidation validation...")
    
    db_path = DATA_DIR / "testrail_data_working.db"
    validator = ConsolidationValidator(db_path)
    
    try:
        validator.connect()
        
        # Run validations
        validator.validate_statistics()
        validator.validate_structure(sample_size=100)
        validator.validate_data_preservation(sample_size=50)
        
        # Spot checks
        spot_checks = validator.spot_check_cases()
        
        # Generate report
        report_path = validator.generate_validation_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Cases:         {validator.validation_results['total_cases']:,}")
        print(f"Consolidated:        {validator.validation_results['consolidated_cases']:,}")
        print(f"Success Rate:        {(validator.validation_results['consolidated_cases'] / validator.validation_results['total_cases'] * 100):.2f}%")
        print(f"Structure Valid:     {validator.validation_results['structure_valid']}/{validator.validation_results['structure_valid'] + validator.validation_results['structure_invalid']}")
        print(f"Data Preserved:      {validator.validation_results['data_preserved']}/{validator.validation_results['data_preserved'] + validator.validation_results['data_loss']}")
        print(f"\nReport saved to: {report_path}")
        
        print("\nSpot Check Results:")
        for check in spot_checks[:3]:
            print(f"  Case {check['case_id']}: ", end="")
            if 'consolidated_structure' in check and isinstance(check['consolidated_structure'], dict):
                s = check['consolidated_structure']
                print(f"{s['preconditions_count']} preconditions, {s['steps_count']} steps, {s['expected_results_count']} expected")
            else:
                print("Check report for details")
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        raise
    finally:
        validator.close()

if __name__ == "__main__":
    main()