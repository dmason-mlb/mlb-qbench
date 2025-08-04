"""Secure path validation to prevent SSRF and directory traversal attacks."""

import os
import stat
from pathlib import Path
from typing import List, Optional
import structlog

logger = structlog.get_logger()


class PathValidationError(Exception):
    """Exception raised when path validation fails."""
    pass


class SecurePathValidator:
    """
    Secure path validator that prevents:
    - Directory traversal attacks
    - Symbolic link attacks
    - SSRF attacks via file:// URLs
    - Access to system files
    """
    
    def __init__(self, allowed_base_dirs: List[str], allowed_extensions: Optional[List[str]] = None):
        """
        Initialize the validator.
        
        Args:
            allowed_base_dirs: List of allowed base directories (absolute paths)
            allowed_extensions: List of allowed file extensions (e.g., ['.json', '.txt'])
        """
        self.allowed_base_dirs = [Path(base_dir).resolve() for base_dir in allowed_base_dirs]
        self.allowed_extensions = allowed_extensions or []
        
        # Ensure all base directories exist and are directories
        for base_dir in self.allowed_base_dirs:
            if not base_dir.exists():
                raise ValueError(f"Base directory does not exist: {base_dir}")
            if not base_dir.is_dir():
                raise ValueError(f"Base path is not a directory: {base_dir}")
    
    def validate_and_resolve_path(self, user_path: str) -> Path:
        """
        Validate and resolve a user-provided path securely.
        
        Args:
            user_path: User-provided path (can be relative or absolute)
            
        Returns:
            Resolved and validated Path object
            
        Raises:
            PathValidationError: If path validation fails
        """
        if not user_path or not user_path.strip():
            raise PathValidationError("Path cannot be empty")
        
        user_path = user_path.strip()
        
        # Check for dangerous patterns
        dangerous_patterns = [
            "..",           # Directory traversal
            "~",            # Home directory
            "file://",      # File URL scheme
            "http://",      # HTTP URL scheme  
            "https://",     # HTTPS URL scheme
            "ftp://",       # FTP URL scheme
            "\x00",         # Null byte
            "|",            # Command injection
            ";",            # Command injection
            "&",            # Command injection
            "`",            # Command injection
            "$(",           # Command substitution
            "${",           # Variable expansion
        ]
        
        for pattern in dangerous_patterns:
            if pattern in user_path:
                logger.warning(
                    "Dangerous pattern detected in path",
                    path=user_path,
                    pattern=pattern,
                    extra={"security_event": True}
                )
                raise PathValidationError(f"Path contains dangerous pattern: {pattern}")
        
        # Convert to path without resolving yet (to check for symlinks first)
        try:
            if os.path.isabs(user_path):
                # Absolute path 
                candidate_path = Path(user_path)
            else:
                # Relative path - join with first allowed base directory  
                candidate_path = self.allowed_base_dirs[0] / user_path
        except (OSError, ValueError) as e:
            logger.warning(
                "Invalid path format",
                path=user_path,
                error=str(e),
                extra={"security_event": True}
            )
            raise PathValidationError(f"Invalid path format: {user_path}")
        
        # Check for symbolic links BEFORE resolving (potential SSRF vector)
        if candidate_path.exists():
            try:
                file_stat = candidate_path.lstat()  # Don't follow symlinks
                if stat.S_ISLNK(file_stat.st_mode):
                    logger.warning(
                        "Symbolic link detected",
                        path=str(candidate_path),
                        extra={"security_event": True}
                    )
                    raise PathValidationError("Symbolic links are not allowed")
            except (OSError, ValueError) as e:
                logger.warning(
                    "Error checking file status",
                    path=str(candidate_path),
                    error=str(e),
                    extra={"security_event": True}
                )
                raise PathValidationError("Unable to validate file status")
        
        # Now resolve the path safely
        try:
            candidate_path = candidate_path.resolve()
        except (OSError, ValueError) as e:
            logger.warning(
                "Path resolution failed",
                path=user_path,
                error=str(e),
                extra={"security_event": True}
            )
            raise PathValidationError(f"Path resolution failed: {user_path}")
        
        # Check if resolved path is within any allowed base directory
        is_within_allowed = False
        for base_dir in self.allowed_base_dirs:
            try:
                candidate_path.relative_to(base_dir)
                is_within_allowed = True
                break
            except ValueError:
                continue
        
        if not is_within_allowed:
            logger.warning(
                "Path outside allowed directories",
                path=str(candidate_path),
                allowed_dirs=[str(d) for d in self.allowed_base_dirs],
                extra={"security_event": True}
            )
            raise PathValidationError("Path is outside allowed directories")
        
        # Check file extension if specified
        if self.allowed_extensions:
            file_suffix = candidate_path.suffix.lower()
            if file_suffix not in self.allowed_extensions:
                logger.warning(
                    "Invalid file extension",
                    path=str(candidate_path),
                    extension=file_suffix,
                    allowed_extensions=self.allowed_extensions,
                    extra={"security_event": True}
                )
                raise PathValidationError(f"File extension '{file_suffix}' not allowed")
        
        # Additional checks for existing files
        if candidate_path.exists():
            # Ensure it's a regular file
            if not candidate_path.is_file():
                raise PathValidationError("Path must point to a regular file")
            
            # Check file size (prevent DoS)
            try:
                file_size = candidate_path.stat().st_size
                if file_size > 100 * 1024 * 1024:  # 100MB limit
                    logger.warning(
                        "File too large",
                        path=str(candidate_path),
                        size=file_size,
                        extra={"security_event": True}
                    )
                    raise PathValidationError("File too large (max 100MB)")
            except (OSError, ValueError) as e:
                raise PathValidationError(f"Unable to check file size: {e}")
        
        logger.info(
            "Path validation successful",
            original_path=user_path,
            resolved_path=str(candidate_path)
        )
        
        return candidate_path


# Global validator instance for data directory
_data_validator: Optional[SecurePathValidator] = None


def get_data_path_validator() -> SecurePathValidator:
    """Get the global data path validator instance."""
    global _data_validator
    if _data_validator is None:
        # Initialize with data directory and JSON extension only
        data_dir = Path("data").resolve()
        _data_validator = SecurePathValidator(
            allowed_base_dirs=[str(data_dir)],
            allowed_extensions=['.json']
        )
    return _data_validator


def validate_data_file_path(user_path: str) -> Path:
    """
    Validate a file path for data ingestion.
    
    Args:
        user_path: User-provided file path
        
    Returns:
        Validated and resolved Path object
        
    Raises:
        PathValidationError: If validation fails
    """
    validator = get_data_path_validator()
    return validator.validate_and_resolve_path(user_path)