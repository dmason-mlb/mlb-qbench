"""Counter service for managing auto-incrementing testIds.

This module provides a thread-safe, persistent counter service for generating unique test IDs.
It uses SQLite for persistence and threading locks for thread safety. The service supports
batch ID reservation for efficient bulk operations.

Dependencies:
    - sqlite3: For persistent storage
    - threading: For thread-safe operations
    - structlog: For logging

Called by:
    - src.ingest.ingest_functional: For assigning unique test IDs during ingestion
    - src.ingest.ingest_api: For batch ID generation during API test ingestion
    - src.models.test_models: For test document ID generation

Complexity:
    - Thread-safe operations: O(1) with lock contention
    - Database operations: O(1) for counter updates
    - Range reservation: O(1) atomic operation
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


class TestIdCounter:
    """Thread-safe counter for generating auto-incrementing test IDs.

    This class provides a persistent, thread-safe counter service using SQLite
    for storage. It supports both single ID generation and bulk range reservation
    for efficient batch operations.

    Thread Safety:
        Uses threading.Lock() to ensure atomic counter operations across threads.

    Persistence:
        Stores counter state in SQLite database with ACID guarantees.

    Performance:
        - Single ID generation: O(1) with minimal lock contention
        - Batch range reservation: O(1) atomic operation
        - Database operations are optimized with prepared statements
    """

    def __init__(self, db_path: Optional[str] = None):
        """Initialize the counter service with a SQLite database.

        Args:
            db_path: Optional path to SQLite database. If None, creates
                    'test_counters.db' in project data directory.

        Complexity: O(1) - Database initialization is constant time

        Side Effects:
            - Creates data directory if it doesn't exist
            - Initializes SQLite database and counter table
            - Sets up threading lock for thread safety
        """
        if db_path is None:
            # Default to a data directory in the project root
            # Path resolution: current_file/../data/test_counters.db
            data_dir = Path(__file__).parent.parent / "data"
            data_dir.mkdir(exist_ok=True)  # Create directory if missing
            db_path = str(data_dir / "test_counters.db")

        self.db_path = db_path
        self._lock = threading.Lock()  # Thread-safe counter operations
        self._init_db()  # Set up database schema and initial values

    def _init_db(self):
        """Initialize the database with the counter table.

        Creates the counters table if it doesn't exist and initializes
        the test_id counter to 0. Uses SQL transactions for consistency.

        Complexity: O(1) - Single table creation and initialization

        Side Effects:
            - Creates 'counters' table with (name, value) schema
            - Inserts initial 'test_id' counter row with value 0
            - Commits transaction for persistence
        """
        with sqlite3.connect(self.db_path) as conn:
            # Create counters table with primary key constraint
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS counters (
                    name TEXT PRIMARY KEY,
                    value INTEGER NOT NULL DEFAULT 0
                )
            """
            )
            # Initialize the test_id counter if it doesn't exist (idempotent)
            conn.execute(
                """
                INSERT OR IGNORE INTO counters (name, value)
                VALUES ('test_id', 0)
            """
            )
            conn.commit()  # Ensure changes are persisted

    def get_next_id(self) -> int:
        """Get the next available test ID (thread-safe).

        Atomically increments the counter and returns the new value.
        This method is thread-safe and guarantees unique IDs across
        concurrent calls.

        Returns:
            int: The next unique test ID (starting from 1)

        Raises:
            RuntimeError: If counter update fails (should not happen)

        Complexity: O(1) - Single atomic database operation

        Thread Safety:
            Uses threading lock to prevent race conditions during
            the increment operation.
        """
        with self._lock:  # Thread-safe critical section
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Increment and return the new value atomically using RETURNING clause
                cursor.execute(
                    """
                    UPDATE counters
                    SET value = value + 1
                    WHERE name = 'test_id'
                    RETURNING value
                """
                )
                result = cursor.fetchone()
                conn.commit()  # Persist the increment

                if result:
                    return result[0]  # Return the new incremented value
                else:
                    # This shouldn't happen if _init_db worked correctly
                    raise RuntimeError("Failed to get next test ID")

    def get_current_id(self) -> int:
        """Get the current counter value without incrementing.

        Returns the current counter value for inspection purposes.
        Does not modify the counter state.

        Returns:
            int: Current counter value (0 if never incremented)

        Complexity: O(1) - Single read-only database query

        Thread Safety:
            Read-only operation, no locking required for consistency.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Read-only query to get current counter value
            cursor.execute(
                """
                SELECT value FROM counters WHERE name = 'test_id'
            """
            )
            result = cursor.fetchone()
            return result[0] if result else 0  # Default to 0 if no record found

    def reset(self, start_value: int = 0):
        """Reset the counter to a specific value (use with caution!).

        WARNING: This operation can lead to ID conflicts if used carelessly.
        Only use for testing or migration scenarios where you're certain
        about the impact.

        Args:
            start_value: New counter value to set (default: 0)

        Complexity: O(1) - Single atomic database update

        Thread Safety:
            Uses threading lock to prevent race conditions during reset.

        Side Effects:
            - Logs warning about counter reset
            - All subsequent IDs will start from start_value + 1
        """
        with self._lock:  # Thread-safe critical section
            with sqlite3.connect(self.db_path) as conn:
                # Atomic update to reset counter value
                conn.execute(
                    """
                    UPDATE counters
                    SET value = ?
                    WHERE name = 'test_id'
                """,
                    (start_value,),
                )
                conn.commit()  # Persist the reset
                logger.warning(f"Test ID counter reset to {start_value}")

    def reserve_range(self, count: int) -> tuple[int, int]:
        """Reserve a range of IDs for batch operations.

        Efficiently reserves a contiguous range of IDs in a single atomic
        operation. This is much more efficient than calling get_next_id()
        multiple times for bulk operations.

        Args:
            count: Number of IDs to reserve (must be > 0)

        Returns:
            Tuple of (start_id, end_id) inclusive. For example,
            reserve_range(3) might return (101, 103) meaning IDs
            101, 102, and 103 are reserved.

        Complexity: O(1) - Single atomic database operation regardless of count

        Thread Safety:
            Uses threading lock to prevent race conditions during reservation.

        Example:
            start, end = counter.reserve_range(100)
            # Use IDs from start to end (inclusive) for batch processing
        """
        with self._lock:  # Thread-safe critical section
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # Get current value before reservation
                cursor.execute(
                    """
                    SELECT value FROM counters WHERE name = 'test_id'
                """
                )
                current = cursor.fetchone()[0]

                # Reserve the range by incrementing counter by count
                new_value = current + count
                cursor.execute(
                    """
                    UPDATE counters
                    SET value = ?
                    WHERE name = 'test_id'
                """,
                    (new_value,),
                )
                conn.commit()  # Persist the reservation

                # Return the range (inclusive start, inclusive end)
                return current + 1, new_value


# Global singleton instance for application-wide counter access
_counter_instance: Optional[TestIdCounter] = None


def get_test_id_counter() -> TestIdCounter:
    """Get the global counter instance (singleton pattern).

    Returns the global TestIdCounter instance, creating it if necessary.
    This ensures a single counter instance across the entire application.

    Returns:
        TestIdCounter: The global counter instance

    Complexity: O(1) - Simple instance check and creation

    Thread Safety:
        Instance creation is not thread-safe, but since this is typically
        called during application startup, it's generally safe in practice.
        For absolute thread safety in creation, consider using a lock.
    """
    global _counter_instance
    if _counter_instance is None:
        _counter_instance = TestIdCounter()
    return _counter_instance
