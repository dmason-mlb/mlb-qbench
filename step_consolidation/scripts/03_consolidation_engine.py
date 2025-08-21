#!/usr/bin/env python3
"""
Main consolidation engine for merging step fields.
Prioritizes accuracy over speed with checkpoint/resume capability.
"""

import sqlite3
import json
import re
import os
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime
from html.parser import HTMLParser
import hashlib
from difflib import SequenceMatcher

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
CHECKPOINT_DIR = BASE_DIR / "checkpoints"

# Create checkpoint directory
CHECKPOINT_DIR.mkdir(exist_ok=True)

# Setup logging
log_file = LOGS_DIR / f"consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
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
    try:
        stripper = HTMLStripper()
        stripper.feed(html_text)
        return stripper.get_text().strip()
    except Exception as e:
        logger.warning(f"HTML stripping failed: {e}")
        return html_text

class StepConsolidator:
    """Consolidates fragmented step fields into unified format."""
    
    def __init__(self, db_path: Path, batch_size: int = 100):
        """
        Initialize consolidator.
        
        Args:
            db_path: Path to database
            batch_size: Number of cases to process in each batch
        """
        self.db_path = db_path
        self.batch_size = batch_size
        self.conn = None
        self.checkpoint_file = CHECKPOINT_DIR / "consolidation_checkpoint.pkl"
        self.error_log_file = LOGS_DIR / f"consolidation_errors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'null_steps': 0,
            'partial_steps': 0,
            'errors': []
        }
        
        # Checkpoint data
        self.checkpoint = {
            'last_processed_id': 0,
            'stats': self.stats,
            'timestamp': None
        }
    
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        logger.info(f"Connected to database: {self.db_path}")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            logger.info("Database connection closed")
    
    def load_checkpoint(self) -> bool:
        """Load checkpoint if exists."""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'rb') as f:
                    self.checkpoint = pickle.load(f)
                    self.stats = self.checkpoint['stats']
                logger.info(f"Checkpoint loaded. Resuming from case ID {self.checkpoint['last_processed_id']}")
                logger.info(f"Previous stats: {self.stats['total_processed']} processed, "
                          f"{self.stats['successful']} successful, {self.stats['failed']} failed")
                return True
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
        return False
    
    def save_checkpoint(self):
        """Save current progress to checkpoint."""
        self.checkpoint['stats'] = self.stats
        self.checkpoint['timestamp'] = datetime.now().isoformat()
        
        try:
            with open(self.checkpoint_file, 'wb') as f:
                pickle.dump(self.checkpoint, f)
            logger.debug(f"Checkpoint saved at case ID {self.checkpoint['last_processed_id']}")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def prepare_database(self):
        """Add consolidated_steps column if not exists."""
        cursor = self.conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(cases)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'consolidated_steps' not in columns:
            logger.info("Adding consolidated_steps column to cases table...")
            cursor.execute("ALTER TABLE cases ADD COLUMN consolidated_steps TEXT")
            self.conn.commit()
            logger.info("Column added successfully")
        else:
            logger.info("consolidated_steps column already exists")
    
    def parse_steps_separated(self, json_text: str) -> List[Dict]:
        """
        Parse steps_separated JSON field.
        
        Returns:
            List of step dictionaries or empty list if parsing fails
        """
        if not json_text or not json_text.strip():
            return []
        
        try:
            data = json.loads(json_text)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # Single step as dict
                return [data]
            else:
                logger.warning(f"Unexpected JSON structure: {type(data)}")
                return []
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error: {e}")
            return []
    
    def extract_given_when_then(self, text: str) -> Dict[str, List[str]]:
        """
        Extract GIVEN/WHEN/THEN patterns from text.
        
        Returns:
            Dictionary with 'given', 'when', 'then' lists
        """
        result = {'given': [], 'when': [], 'then': []}
        
        if not text:
            return result
        
        # Clean text
        text = strip_html(text)
        
        # Split by common patterns
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for patterns
            if re.match(r'^GIVEN\b', line, re.IGNORECASE):
                result['given'].append(line)
            elif re.match(r'^WHEN\b', line, re.IGNORECASE):
                result['when'].append(line)
            elif re.match(r'^THEN\b', line, re.IGNORECASE):
                result['then'].append(line)
            elif re.match(r'^AND\b', line, re.IGNORECASE):
                # Add to the last category that had content
                if result['then']:
                    result['then'].append(line)
                elif result['when']:
                    result['when'].append(line)
                elif result['given']:
                    result['given'].append(line)
        
        return result
    
    def deduplicate_content(self, items: List[str], threshold: float = 0.85) -> List[str]:
        """
        Remove duplicate or highly similar content.
        
        Args:
            items: List of text items
            threshold: Similarity threshold (0-1)
        
        Returns:
            Deduplicated list
        """
        if len(items) <= 1:
            return items
        
        unique = []
        for item in items:
            is_duplicate = False
            for unique_item in unique:
                similarity = SequenceMatcher(None, item.lower(), unique_item.lower()).ratio()
                if similarity >= threshold:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique.append(item)
        
        return unique
    
    def consolidate_case(self, case: sqlite3.Row) -> Optional[Dict]:
        """
        Consolidate step fields for a single case.
        
        Returns:
            Consolidated data dictionary or None if no steps exist
        """
        case_id = case['id']
        steps = case['steps']
        steps_separated = case['steps_separated']
        steps_combined = case['steps_combined']
        
        # Check if all fields are empty
        if not any([steps, steps_separated, steps_combined]):
            return None
        
        # Initialize consolidated structure
        consolidated = {
            'preconditions': [],
            'steps': [],
            'expected_results': [],
            'metadata': {
                'source_fields': [],
                'consolidation_timestamp': datetime.now().isoformat(),
                'has_json_structure': False,
                'has_html_content': False
            }
        }
        
        # Process steps_combined (often contains preconditions)
        if steps_combined and steps_combined.strip():
            consolidated['metadata']['source_fields'].append('steps_combined')
            
            # Check for HTML
            if '<' in steps_combined and '>' in steps_combined:
                consolidated['metadata']['has_html_content'] = True
            
            # Extract patterns
            patterns = self.extract_given_when_then(steps_combined)
            consolidated['preconditions'].extend(patterns['given'])
            consolidated['steps'].extend(patterns['when'])
            consolidated['expected_results'].extend(patterns['then'])
            
            # If no patterns found, treat as general steps
            if not any([patterns['given'], patterns['when'], patterns['then']]):
                clean_text = strip_html(steps_combined).strip()
                if clean_text:
                    # Check if it looks like preconditions
                    if any(word in clean_text.lower() for word in ['given', 'prerequisite', 'precondition']):
                        consolidated['preconditions'].append(clean_text)
                    else:
                        consolidated['steps'].append(clean_text)
        
        # Process steps field (summary)
        if steps and steps.strip():
            consolidated['metadata']['source_fields'].append('steps')
            
            # Check for HTML
            if '<' in steps and '>' in steps:
                consolidated['metadata']['has_html_content'] = True
            
            clean_text = strip_html(steps).strip()
            if clean_text:
                # Don't add if it's already in consolidated content
                existing_text = ' '.join(consolidated['steps'] + consolidated['preconditions'])
                if clean_text not in existing_text:
                    consolidated['steps'].append(clean_text)
        
        # Process steps_separated (JSON with detailed steps)
        if steps_separated and steps_separated.strip():
            consolidated['metadata']['source_fields'].append('steps_separated')
            
            json_steps = self.parse_steps_separated(steps_separated)
            if json_steps:
                consolidated['metadata']['has_json_structure'] = True
                
                for step in json_steps:
                    if isinstance(step, dict):
                        content = step.get('content', '').strip()
                        expected = step.get('expected', '').strip()
                        
                        if content:
                            # Check for WHEN pattern
                            if re.match(r'^WHEN\b', content, re.IGNORECASE):
                                consolidated['steps'].append(content)
                            else:
                                # Default to steps
                                consolidated['steps'].append(content)
                        
                        if expected:
                            # Check for THEN pattern
                            if re.match(r'^THEN\b', expected, re.IGNORECASE):
                                consolidated['expected_results'].append(expected)
                            else:
                                # Default to expected results
                                consolidated['expected_results'].append(expected)
        
        # Deduplicate content
        consolidated['preconditions'] = self.deduplicate_content(consolidated['preconditions'])
        consolidated['steps'] = self.deduplicate_content(consolidated['steps'])
        consolidated['expected_results'] = self.deduplicate_content(consolidated['expected_results'])
        
        # Check if we have any content
        if not any([consolidated['preconditions'], consolidated['steps'], consolidated['expected_results']]):
            return None
        
        return consolidated
    
    def format_consolidated_output(self, consolidated: Dict) -> str:
        """
        Format consolidated data as structured JSON string.
        """
        return json.dumps(consolidated, indent=2, ensure_ascii=False)
    
    def process_batch(self, start_id: int) -> int:
        """
        Process a batch of cases.
        
        Returns:
            Number of cases processed
        """
        cursor = self.conn.cursor()
        
        # Get batch of cases
        query = """
        SELECT id, steps, steps_separated, steps_combined
        FROM cases
        WHERE id > ?
        ORDER BY id
        LIMIT ?
        """
        cursor.execute(query, (start_id, self.batch_size))
        cases = cursor.fetchall()
        
        if not cases:
            return 0
        
        processed = 0
        for case in cases:
            case_id = case['id']
            
            try:
                # Consolidate fields
                consolidated = self.consolidate_case(case)
                
                if consolidated is None:
                    # No steps to consolidate
                    self.stats['null_steps'] += 1
                    logger.debug(f"Case {case_id}: No steps found")
                else:
                    # Format and save
                    consolidated_json = self.format_consolidated_output(consolidated)
                    
                    # Update database
                    update_query = "UPDATE cases SET consolidated_steps = ? WHERE id = ?"
                    cursor.execute(update_query, (consolidated_json, case_id))
                    
                    self.stats['successful'] += 1
                    
                    # Check if partial (missing some expected content)
                    if len(consolidated['metadata']['source_fields']) < 2:
                        self.stats['partial_steps'] += 1
                
                processed += 1
                self.stats['total_processed'] += 1
                self.checkpoint['last_processed_id'] = case_id
                
            except Exception as e:
                logger.error(f"Error processing case {case_id}: {e}")
                self.stats['failed'] += 1
                self.stats['errors'].append({
                    'case_id': case_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        # Commit changes
        self.conn.commit()
        
        # Save checkpoint every batch
        self.save_checkpoint()
        
        return processed
    
    def run_consolidation(self):
        """Run the full consolidation process."""
        logger.info("Starting consolidation process...")
        
        # Load checkpoint if exists
        resuming = self.load_checkpoint()
        start_id = self.checkpoint['last_processed_id'] if resuming else 0
        
        # Get total count
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM cases WHERE id > ?", (start_id,))
        remaining = cursor.fetchone()[0]
        
        logger.info(f"Cases to process: {remaining}")
        
        # Process in batches
        batch_num = 0
        while True:
            batch_num += 1
            processed = self.process_batch(start_id)
            
            if processed == 0:
                break
            
            start_id = self.checkpoint['last_processed_id']
            
            # Log progress
            if batch_num % 10 == 0:
                logger.info(f"Progress: {self.stats['total_processed']} processed, "
                          f"{self.stats['successful']} successful, "
                          f"{self.stats['failed']} failed, "
                          f"{self.stats['null_steps']} null")
        
        logger.info("Consolidation complete!")
        return self.stats
    
    def generate_final_report(self):
        """Generate final consolidation report."""
        report_path = REPORTS_DIR / f"consolidation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("STEP FIELD CONSOLIDATION REPORT\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("STATISTICS\n")
            f.write("-" * 40 + "\n")
            f.write(f"Total Processed:     {self.stats['total_processed']:,}\n")
            f.write(f"Successful:          {self.stats['successful']:,}\n")
            f.write(f"Failed:              {self.stats['failed']:,}\n")
            f.write(f"Null Steps:          {self.stats['null_steps']:,}\n")
            f.write(f"Partial Steps:       {self.stats['partial_steps']:,}\n")
            
            if self.stats['total_processed'] > 0:
                success_rate = (self.stats['successful'] / self.stats['total_processed']) * 100
                f.write(f"\nSuccess Rate:        {success_rate:.2f}%\n")
            
            if self.stats['errors']:
                f.write(f"\nERRORS (First 20)\n")
                f.write("-" * 40 + "\n")
                for error in self.stats['errors'][:20]:
                    f.write(f"Case {error['case_id']}: {error['error']}\n")
            
            # Save errors to JSON for detailed analysis
            if self.stats['errors']:
                with open(self.error_log_file, 'w') as ef:
                    json.dump(self.stats['errors'], ef, indent=2)
                f.write(f"\nFull error log saved to: {self.error_log_file}\n")
        
        logger.info(f"Report generated: {report_path}")
        return report_path

def main():
    """Main execution function."""
    db_path = DATA_DIR / "testrail_data_working.db"
    
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return
    
    consolidator = StepConsolidator(db_path, batch_size=100)
    
    try:
        consolidator.connect()
        consolidator.prepare_database()
        
        # Run consolidation
        stats = consolidator.run_consolidation()
        
        # Generate report
        report_path = consolidator.generate_final_report()
        
        print("\n" + "=" * 60)
        print("CONSOLIDATION COMPLETE")
        print("=" * 60)
        print(f"Total Processed: {stats['total_processed']:,}")
        print(f"Successful:      {stats['successful']:,}")
        print(f"Failed:          {stats['failed']:,}")
        print(f"Null Steps:      {stats['null_steps']:,}")
        if stats['total_processed'] > 0:
            success_rate = (stats['successful'] / stats['total_processed']) * 100
            print(f"Success Rate:    {success_rate:.2f}%")
        print(f"\nReport saved to: {report_path}")
        
    except Exception as e:
        logger.error(f"Consolidation failed: {e}", exc_info=True)
        raise
    finally:
        consolidator.close()

if __name__ == "__main__":
    main()