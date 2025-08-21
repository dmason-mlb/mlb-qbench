"""Secure path validation to prevent SSRF and directory traversal attacks.

This module provides comprehensive path validation to protect against:
- Directory traversal attacks (../../../etc/passwd)
- Symbolic link attacks (symlink to sensitive files)
- SSRF attacks via file:// URLs
- Command injection via special characters
- Access to system files outside allowed directories

Security Features:
    - Pattern-based dangerous string detection
    - Symbolic link validation before resolution
    - Directory boundary enforcement using relative_to()
    - File extension whitelisting
    - File size limits (DoS prevention)
    - Comprehensive security event logging

Dependencies:
    - os: For file system operations and stat checks
    - stat: For symbolic link detection via S_ISLNK
    - pathlib: For secure path resolution and manipulation
    - structlog: For security event logging

Called by:
    - src.ingest.ingest_functional: For validating test data file paths
    - src.ingest.ingest_api: For validating API test data paths
    - src.service.main: For validating user-provided file paths

Complexity:
    - Path validation: O(n) where n is path length + pattern count
    - Directory traversal check: O(d) where d is directory depth
    - Extension validation: O(1) string comparison
"""

import os
import stat
from pathlib import Path
from typing import Optional

import structlog

logger = structlog.get_logger()


class PathValidationError(Exception):
    """Exception raised when path validation fails.

    This exception is raised when any security validation check fails,
    including directory traversal attempts, symbolic link detection,
    dangerous pattern matches, or boundary violations.
    """

    pass


class SecurePathValidator:
    """Secure path validator that prevents multiple attack vectors.

    This class implements defense-in-depth security for file path validation:
    - Directory traversal attacks (../, ~/, etc.)
    - Symbolic link attacks (symlink to sensitive files)
    - SSRF attacks via file:// and http:// URLs
    - Command injection via special characters
    - Access to system files outside allowed directories
    - DoS attacks via oversized files

    Security Model:
        1. Pattern-based dangerous string detection
        2. Symbolic link check before resolution
        3. Path resolution with boundary enforcement
        4. Extension and size validation
        5. Comprehensive security logging

    Performance:
        - Initialization: O(d) where d is number of base directories
        - Validation: O(n*p + d) where n=path length, p=patterns, d=directories
    """

    def __init__(
        self, allowed_base_dirs: list[str], allowed_extensions: Optional[list[str]] = None
    ):
        """Initialize the validator with security constraints.

        Args:
            allowed_base_dirs: List of allowed base directories (absolute paths).
                              All file access is restricted to these directories.
            allowed_extensions: Optional list of allowed file extensions
                              (e.g., ['.json', '.txt']). If None, all extensions allowed.

        Raises:
            ValueError: If any base directory doesn't exist or isn't a directory

        Complexity: O(d) where d is number of base directories to validate

        Security Notes:
            - Base directories are resolved to prevent symlink attacks
            - All directories must exist and be actual directories
            - Validation happens at initialization for fail-fast behavior
        """
        # Resolve base directories to canonical form (prevents symlink attacks)
        self.allowed_base_dirs = [Path(base_dir).resolve() for base_dir in allowed_base_dirs]
        self.allowed_extensions = allowed_extensions or []

        # Validate all base directories exist and are actual directories
        for base_dir in self.allowed_base_dirs:
            if not base_dir.exists():
                raise ValueError(f"Base directory does not exist: {base_dir}")
            if not base_dir.is_dir():
                raise ValueError(f"Base path is not a directory: {base_dir}")

    def validate_and_resolve_path(self, user_path: str) -> Path:
        """Validate and resolve a user-provided path securely.

        This method implements a multi-stage security validation process:
        1. Input sanitization and dangerous pattern detection
        2. Path construction and symbolic link checks
        3. Secure path resolution
        4. Directory boundary enforcement
        5. Extension and file size validation

        Args:
            user_path: User-provided path (can be relative or absolute).
                      Relative paths are joined with the first allowed base directory.

        Returns:
            Resolved and validated Path object that is guaranteed to be:
            - Within allowed base directories
            - Free of dangerous patterns
            - Not a symbolic link
            - Within size limits (if file exists)
            - Has allowed extension (if restrictions apply)

        Raises:
            PathValidationError: If any validation step fails, including:
                - Empty or invalid path format
                - Dangerous patterns detected
                - Symbolic links found
                - Path outside allowed directories
                - Invalid file extension
                - File too large (>100MB)

        Complexity: O(n*p + d + f) where:
            - n = path length
            - p = number of dangerous patterns (18 patterns)
            - d = number of allowed directories
            - f = file system operations (stat, resolve)

        Security Flow:
            Input → Pattern Check → Path Construction → Symlink Check →
            Resolution → Boundary Check → Extension Check → Size Check → Output
        """
        # Step 1: Input validation and sanitization
        if not user_path or not user_path.strip():
            raise PathValidationError("Path cannot be empty")

        user_path = user_path.strip()  # Remove leading/trailing whitespace

        # Step 2: Dangerous pattern detection (defense against multiple attack vectors)
        dangerous_patterns = [
            "..",  # Directory traversal attack
            "~",  # Home directory access
            "file://",  # File URL scheme (SSRF prevention)
            "http://",  # HTTP URL scheme (SSRF prevention)
            "https://",  # HTTPS URL scheme (SSRF prevention)
            "ftp://",  # FTP URL scheme (SSRF prevention)
            "\x00",  # Null byte injection
            "|",  # Command injection via pipe
            ";",  # Command injection via semicolon
            "&",  # Command injection via ampersand
            "`",  # Command injection via backtick
            "$(",  # Command substitution
            "${",  # Variable expansion
        ]

        # Pattern matching - O(n*p) where n=path length, p=pattern count
        for pattern in dangerous_patterns:
            if pattern in user_path:
                # Log security event with context for monitoring
                logger.warning(
                    "Dangerous pattern detected in path",
                    path=user_path,
                    pattern=pattern,
                    extra={"security_event": True},
                )
                raise PathValidationError(f"Path contains dangerous pattern: {pattern}")

        # Step 3: Path construction without resolution (prevents premature symlink following)
        try:
            if os.path.isabs(user_path):
                # Absolute path - use as-is but don't resolve yet
                candidate_path = Path(user_path)
            else:
                # Relative path - join with first allowed base directory
                # This constrains relative paths to allowed areas
                candidate_path = self.allowed_base_dirs[0] / user_path
        except (OSError, ValueError) as e:
            logger.warning(
                "Invalid path format", path=user_path, error=str(e), extra={"security_event": True}
            )
            raise PathValidationError(f"Invalid path format: {user_path}") from None

        # Step 4: Symbolic link detection BEFORE resolution (critical security check)
        # This prevents SSRF attacks via symlinks to /proc/net/tcp, /etc/passwd, etc.
        if candidate_path.exists():
            try:
                # Use lstat() to get link metadata without following the link
                file_stat = candidate_path.lstat()  # Don't follow symlinks
                if stat.S_ISLNK(file_stat.st_mode):
                    logger.warning(
                        "Symbolic link detected",
                        path=str(candidate_path),
                        extra={"security_event": True},
                    )
                    raise PathValidationError("Symbolic links are not allowed")
            except (OSError, ValueError) as e:
                logger.warning(
                    "Error checking file status",
                    path=str(candidate_path),
                    error=str(e),
                    extra={"security_event": True},
                )
                raise PathValidationError("Unable to validate file status") from None

        # Step 5: Safe path resolution (now that symlinks are verified)
        try:
            # resolve() canonicalizes the path and follows any remaining links
            # This is safe now because we've already checked for dangerous symlinks
            candidate_path = candidate_path.resolve()
        except (OSError, ValueError) as e:
            logger.warning(
                "Path resolution failed",
                path=user_path,
                error=str(e),
                extra={"security_event": True},
            )
            raise PathValidationError(f"Path resolution failed: {user_path}") from None

        # Step 6: Directory boundary enforcement (critical security check)
        # Verify the resolved path is within allowed base directories
        is_within_allowed = False
        for base_dir in self.allowed_base_dirs:
            try:
                # relative_to() raises ValueError if path is outside base_dir
                # This is the key security check against directory traversal
                candidate_path.relative_to(base_dir)
                is_within_allowed = True
                break  # Found valid base directory, no need to check others
            except ValueError:
                # Path is not within this base directory, try next one
                continue

        if not is_within_allowed:
            logger.warning(
                "Path outside allowed directories",
                path=str(candidate_path),
                allowed_dirs=[str(d) for d in self.allowed_base_dirs],
                extra={"security_event": True},
            )
            raise PathValidationError("Path is outside allowed directories")

        # Step 7: File extension validation (if restrictions are configured)
        if self.allowed_extensions:
            file_suffix = candidate_path.suffix.lower()  # Case-insensitive check
            if file_suffix not in self.allowed_extensions:
                logger.warning(
                    "Invalid file extension",
                    path=str(candidate_path),
                    extension=file_suffix,
                    allowed_extensions=self.allowed_extensions,
                    extra={"security_event": True},
                )
                raise PathValidationError(f"File extension '{file_suffix}' not allowed")

        # Step 8: Additional file-specific security checks (for existing files)
        if candidate_path.exists():
            # Ensure it's a regular file (not directory, device, fifo, etc.)
            if not candidate_path.is_file():
                raise PathValidationError("Path must point to a regular file")

            # File size check (DoS prevention via large file uploads)
            try:
                file_size = candidate_path.stat().st_size
                # 100MB limit prevents memory exhaustion during file processing
                if file_size > 100 * 1024 * 1024:  # 100MB limit
                    logger.warning(
                        "File too large",
                        path=str(candidate_path),
                        size=file_size,
                        extra={"security_event": True},
                    )
                    raise PathValidationError("File too large (max 100MB)")
            except (OSError, ValueError) as e:
                raise PathValidationError(f"Unable to check file size: {e}") from e

        # Log successful validation for audit trail
        logger.info(
            "Path validation successful", original_path=user_path, resolved_path=str(candidate_path)
        )

        return candidate_path


# Global singleton validator instance for data directory access
_data_validator: Optional[SecurePathValidator] = None


def get_data_path_validator() -> SecurePathValidator:
    """Get the global data path validator instance (singleton pattern).

    Returns a preconfigured validator for the application's data directory
    that only allows JSON files within the 'data' directory.

    Returns:
        SecurePathValidator: Configured for data directory with JSON-only access

    Complexity: O(1) - Simple instance check and creation

    Thread Safety:
        Instance creation is not thread-safe, but since this is typically
        called during application startup, it's generally safe in practice.
    """
    global _data_validator
    if _data_validator is None:
        # Initialize with data directory and JSON extension only
        # This restricts all data ingestion to JSON files in the data directory
        data_dir = Path("data").resolve()
        _data_validator = SecurePathValidator(
            allowed_base_dirs=[str(data_dir)],
            allowed_extensions=[".json"],  # Only JSON files allowed for data ingestion
        )
    return _data_validator


def validate_data_file_path(user_path: str) -> Path:
    """Validate a file path for data ingestion operations.

    Convenience function that uses the global data path validator to
    validate file paths for test data ingestion. Ensures files are:
    - Within the 'data' directory
    - Have .json extension
    - Pass all security checks

    Args:
        user_path: User-provided file path (relative to data dir or absolute)

    Returns:
        Validated and resolved Path object guaranteed to be secure

    Raises:
        PathValidationError: If validation fails for any security reason

    Complexity: O(n*p + d + f) - Same as validate_and_resolve_path()

    Usage:
        path = validate_data_file_path("tests/api_tests.json")
        # Returns: /absolute/path/to/data/tests/api_tests.json
    """
    validator = get_data_path_validator()
    return validator.validate_and_resolve_path(user_path)
