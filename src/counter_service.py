"""Counter service for managing auto-incrementing testIds."""

import os
import sqlite3
import threading
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


class TestIdCounter:
    """Thread-safe counter for generating auto-incrementing test IDs."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the counter service with a SQLite database."""
        if db_path is None:
            # Default to a data directory in the project root
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "test_counters.db")
        
        self.db_path = db_path
        self._lock = threading.Lock()
        self._init_db()
        
    def _init_db(self):
        """Initialize the database with the counter table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS counters (
                    name TEXT PRIMARY KEY,
                    value INTEGER NOT NULL DEFAULT 0
                )
            """)
            # Initialize the test_id counter if it doesn't exist
            conn.execute("""
                INSERT OR IGNORE INTO counters (name, value) 
                VALUES ('test_id', 0)
            """)
            conn.commit()
            
    def get_next_id(self) -> int:
        """Get the next available test ID (thread-safe)."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Increment and return the new value atomically
                cursor.execute("""
                    UPDATE counters 
                    SET value = value + 1 
                    WHERE name = 'test_id'
                    RETURNING value
                """)
                result = cursor.fetchone()
                conn.commit()
                
                if result:
                    return result[0]
                else:
                    # This shouldn't happen, but handle it gracefully
                    raise RuntimeError("Failed to get next test ID")
                    
    def get_current_id(self) -> int:
        """Get the current counter value without incrementing."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM counters WHERE name = 'test_id'
            """)
            result = cursor.fetchone()
            return result[0] if result else 0
            
    def reset(self, start_value: int = 0):
        """Reset the counter to a specific value (use with caution!)."""
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE counters 
                    SET value = ? 
                    WHERE name = 'test_id'
                """, (start_value,))
                conn.commit()
                logger.warning(f"Test ID counter reset to {start_value}")
                
    def reserve_range(self, count: int) -> tuple[int, int]:
        """Reserve a range of IDs for batch operations.
        
        Returns:
            Tuple of (start_id, end_id) inclusive.
        """
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get current value
                cursor.execute("""
                    SELECT value FROM counters WHERE name = 'test_id'
                """)
                current = cursor.fetchone()[0]
                
                # Reserve the range
                new_value = current + count
                cursor.execute("""
                    UPDATE counters 
                    SET value = ? 
                    WHERE name = 'test_id'
                """, (new_value,))
                conn.commit()
                
                # Return the range (exclusive start, inclusive end)
                return current + 1, new_value


# Global instance
_counter_instance: Optional[TestIdCounter] = None


def get_test_id_counter() -> TestIdCounter:
    """Get the global counter instance."""
    global _counter_instance
    if _counter_instance is None:
        _counter_instance = TestIdCounter()
    return _counter_instance