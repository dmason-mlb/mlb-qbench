"""JIRA key validation to prevent injection attacks and ensure format compliance.

This module provides comprehensive validation for JIRA issue keys to protect against:
- SQL injection attacks via malicious characters
- XSS attacks through script injection
- Command injection via shell metacharacters
- CRLF injection for HTTP header manipulation
- URL manipulation attacks
- DoS attacks via oversized input

Security Features:
    - Strict format validation using regex patterns
    - Dangerous character detection and blocking
    - Length limits to prevent DoS attacks
    - Comprehensive security event logging
    - Format compliance with JIRA standards

JIRA Key Format:
    - Standard format: PROJECT-123
    - Project key: 2-10 uppercase letters/numbers, starts with letter
    - Issue number: 1-8 digits, cannot start with 0
    - Total length: Maximum 20 characters

Dependencies:
    - re: For regex pattern matching
    - structlog: For security event logging

Called by:
    - src.service.main: For validating JIRA keys in API requests
    - src.models.test_models: For validating JIRA keys in test documents
    - src.ingest modules: For validating JIRA keys during data ingestion

Complexity:
    - Pattern matching: O(n) where n is key length
    - Character validation: O(n*c) where c is dangerous character count
    - Overall validation: O(n) linear time complexity
"""

import re
from typing import Optional

import structlog

logger = structlog.get_logger()


class JiraKeyValidationError(Exception):
    """Exception raised when JIRA key validation fails.
    
    This exception is raised when any JIRA key validation check fails,
    including format violations, dangerous character detection, length
    limits, or injection attempt detection.
    """
    pass


class JiraKeyValidator:
    """Validator for JIRA keys to prevent injection attacks and ensure proper format.
    
    This class implements comprehensive security validation for JIRA issue keys:
    - Format compliance with JIRA standards (PROJECT-123 pattern)
    - Injection attack prevention via dangerous character detection
    - DoS protection through length limits
    - Security event logging for monitoring
    
    JIRA Key Format Rules:
        - Project key: 2-10 characters, starts with letter, uppercase letters/numbers only
        - Separator: Single hyphen (-)
        - Issue number: 1-8 digits, cannot start with 0 (1-99999999 range)
        - Total length: Maximum 20 characters
        
    Security Model:
        1. Length validation (DoS prevention)
        2. Dangerous character detection (injection prevention)
        3. Format validation using regex (compliance enforcement)
        4. Project key length validation (additional check)
        5. Security event logging (monitoring)
    
    Performance:
        - Validation: O(n) where n is key length
        - Pattern matching: Single regex operation
        - Character scanning: Linear pass through input
    """

    # Standard JIRA key pattern: PROJECT-123
    # ^[A-Z]       - Must start with uppercase letter
    # [A-Z0-9]{1,9} - 1-9 additional uppercase letters or numbers (total 2-10)
    # -            - Literal hyphen separator
    # [1-9]        - First digit must be 1-9 (not 0)
    # [0-9]{0,7}   - 0-7 additional digits (total 1-8 digits)
    # $            - End of string
    JIRA_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9]{1,9}-[1-9][0-9]{0,7}$')

    # Maximum length to prevent DoS attacks
    MAX_LENGTH = 20

    def __init__(self):
        """Initialize the JIRA key validator.
        
        Creates a new validator instance with predefined security rules.
        No configuration needed as JIRA key format is standardized.
        
        Complexity: O(1) - Simple initialization with no setup required
        """
        pass

    def validate_jira_key(self, jira_key: str) -> str:
        """Validate a JIRA key format and content comprehensively.
        
        Performs multi-stage security validation to ensure the JIRA key is:
        - Not empty or oversized (DoS protection)
        - Free of dangerous characters (injection prevention)
        - Compliant with JIRA format standards
        - Has valid project key length
        
        Args:
            jira_key: The JIRA key to validate (e.g., "PROJECT-123")

        Returns:
            The validated JIRA key (unchanged if valid)

        Raises:
            JiraKeyValidationError: If any validation step fails:
                - Empty key
                - Oversized key (>20 chars)
                - Dangerous characters detected
                - Invalid format pattern
                - Project key too short (<2 chars)
                
        Complexity: O(n) where n is key length
        
        Security Flow:
            Input → Length Check → Character Scan → Pattern Match → 
            Project Key Check → Output
        """
        # Step 1: Input validation (empty check)
        if not jira_key:
            raise JiraKeyValidationError("JIRA key cannot be empty")

        # Step 2: Length validation (DoS protection)
        if len(jira_key) > self.MAX_LENGTH:
            # Truncate key in logs to prevent log injection
            logger.warning(
                "JIRA key too long",
                key=jira_key[:20] + "..." if len(jira_key) > 20 else jira_key,
                length=len(jira_key),
                extra={"security_event": True}
            )
            raise JiraKeyValidationError("JIRA key too long")

        # Step 3: Dangerous character detection (injection prevention)
        # Comprehensive list of characters that could be used in various attacks
        dangerous_chars = [
            "'", '"',        # SQL injection quotes
            "<", ">",        # XSS angle brackets
            "&", "|",        # Command injection operators
            ";", "(",        # Command injection delimiters
            ")", "{",        # Command injection braces
            "}", "[",        # Command injection brackets
            "]", "\\",       # Path traversal backslash
            "/", "?",        # URL manipulation characters
            "#", "%",        # URL encoding characters
            "\n", "\r",      # CRLF injection newlines
            "\t", "\x00"     # Control characters (tab, null)
        ]

        # Scan for dangerous characters - O(n*c) where n=key length, c=char count
        for char in dangerous_chars:
            if char in jira_key:
                # Log security event with character representation for clarity
                logger.warning(
                    "Dangerous character in JIRA key",
                    key=jira_key,
                    character=repr(char),  # repr() shows escape sequences
                    extra={"security_event": True}
                )
                raise JiraKeyValidationError(f"JIRA key contains invalid character: {repr(char)}")

        # Step 4: Format validation using regex pattern matching
        if not self.JIRA_KEY_PATTERN.match(jira_key):
            logger.warning(
                "Invalid JIRA key format",
                key=jira_key,
                expected_format="PROJECT-123",
                extra={"security_event": True}
            )
            raise JiraKeyValidationError(
                "Invalid JIRA key format. Expected format: PROJECT-123 "
                "(2-10 uppercase letters/numbers, hyphen, 1-8 digits)"
            )

        # Step 5: Additional project key validation (redundant but explicit check)
        # This is technically covered by the regex, but provides clearer error messaging
        project_key = jira_key.split('-')[0]  # Extract project part before hyphen
        if len(project_key) < 2:
            raise JiraKeyValidationError("Project key must be at least 2 characters")

        # Log successful validation for audit trail
        logger.debug(
            "JIRA key validation successful",
            key=jira_key,
            project=project_key
        )

        return jira_key  # Return unchanged validated key

    def is_valid_jira_key_format(self, jira_key: str) -> bool:
        """Check if a JIRA key has valid format without raising exceptions.
        
        Convenience method that performs full validation but returns a boolean
        instead of raising exceptions. Useful for conditional logic where
        exception handling would be cumbersome.
        
        Args:
            jira_key: The JIRA key to check (same format as validate_jira_key)

        Returns:
            True if format is valid and passes all security checks,
            False if any validation step fails
            
        Complexity: O(n) - Same as validate_jira_key but with exception handling
        
        Usage:
            if validator.is_valid_jira_key_format("PROJECT-123"):
                # Process valid key
            else:
                # Handle invalid key
        """
        try:
            # Delegate to full validation method
            self.validate_jira_key(jira_key)
            return True  # All validation steps passed
        except JiraKeyValidationError:
            # Any validation failure results in False
            return False


# Global singleton validator instance for application-wide use
_jira_validator: Optional[JiraKeyValidator] = None


def get_jira_validator() -> JiraKeyValidator:
    """Get the global JIRA key validator instance (singleton pattern).
    
    Returns the global JiraKeyValidator instance, creating it if necessary.
    This ensures consistent validation rules across the entire application.
    
    Returns:
        JiraKeyValidator: The global validator instance
        
    Complexity: O(1) - Simple instance check and creation
    
    Thread Safety:
        Instance creation is not thread-safe, but since this is typically
        called during application startup, it's generally safe in practice.
    """
    global _jira_validator
    if _jira_validator is None:
        _jira_validator = JiraKeyValidator()
    return _jira_validator


def validate_jira_key(jira_key: str) -> str:
    """Validate a JIRA key using the global validator instance.
    
    Convenience function that uses the global validator to validate JIRA keys.
    This is the primary entry point for JIRA key validation throughout the
    application.
    
    Args:
        jira_key: The JIRA key to validate (e.g., "PROJECT-123")

    Returns:
        The validated JIRA key (unchanged if valid)

    Raises:
        JiraKeyValidationError: If validation fails for any security reason
        
    Complexity: O(n) - Same as JiraKeyValidator.validate_jira_key()
    
    Usage:
        try:
            valid_key = validate_jira_key(user_input)
            # Use valid_key safely
        except JiraKeyValidationError as e:
            # Handle validation error
    """
    validator = get_jira_validator()
    return validator.validate_jira_key(jira_key)
