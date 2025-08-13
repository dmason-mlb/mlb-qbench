"""JIRA key validation to prevent injection attacks and ensure format compliance."""

import re
from typing import Optional

import structlog

logger = structlog.get_logger()


class JiraKeyValidationError(Exception):
    """Exception raised when JIRA key validation fails."""
    pass


class JiraKeyValidator:
    """
    Validator for JIRA keys to prevent injection attacks and ensure proper format.

    JIRA key format: PROJECT-123 (project key followed by hyphen and number)
    - Project key: 2-10 uppercase letters/numbers
    - Issue number: 1-8 digits
    """

    # Standard JIRA key pattern: PROJECT-123
    JIRA_KEY_PATTERN = re.compile(r'^[A-Z][A-Z0-9]{1,9}-[1-9][0-9]{0,7}$')

    # Maximum length to prevent DoS
    MAX_LENGTH = 20

    def __init__(self):
        """Initialize the JIRA key validator."""
        pass

    def validate_jira_key(self, jira_key: str) -> str:
        """
        Validate a JIRA key format and content.

        Args:
            jira_key: The JIRA key to validate

        Returns:
            The validated JIRA key (unchanged if valid)

        Raises:
            JiraKeyValidationError: If validation fails
        """
        if not jira_key:
            raise JiraKeyValidationError("JIRA key cannot be empty")

        # Check length to prevent DoS
        if len(jira_key) > self.MAX_LENGTH:
            logger.warning(
                "JIRA key too long",
                key=jira_key[:20] + "..." if len(jira_key) > 20 else jira_key,
                length=len(jira_key),
                extra={"security_event": True}
            )
            raise JiraKeyValidationError("JIRA key too long")

        # Check for dangerous characters that could indicate injection
        dangerous_chars = [
            "'", '"',        # SQL injection
            "<", ">",        # XSS
            "&", "|",        # Command injection
            ";", "(",        # Command injection
            ")", "{",        # Command injection
            "}", "[",        # Command injection
            "]", "\\",       # Path traversal
            "/", "?",        # URL manipulation
            "#", "%",        # URL encoding
            "\n", "\r",      # CRLF injection
            "\t", "\x00"     # Control characters
        ]

        for char in dangerous_chars:
            if char in jira_key:
                logger.warning(
                    "Dangerous character in JIRA key",
                    key=jira_key,
                    character=repr(char),
                    extra={"security_event": True}
                )
                raise JiraKeyValidationError(f"JIRA key contains invalid character: {repr(char)}")

        # Validate format using regex
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

        # Additional project key validation
        project_key = jira_key.split('-')[0]
        if len(project_key) < 2:
            raise JiraKeyValidationError("Project key must be at least 2 characters")

        # Log successful validation
        logger.debug(
            "JIRA key validation successful",
            key=jira_key,
            project=project_key
        )

        return jira_key

    def is_valid_jira_key_format(self, jira_key: str) -> bool:
        """
        Check if a JIRA key has valid format without raising exceptions.

        Args:
            jira_key: The JIRA key to check

        Returns:
            True if format is valid, False otherwise
        """
        try:
            self.validate_jira_key(jira_key)
            return True
        except JiraKeyValidationError:
            return False


# Global validator instance
_jira_validator: Optional[JiraKeyValidator] = None


def get_jira_validator() -> JiraKeyValidator:
    """Get the global JIRA key validator instance."""
    global _jira_validator
    if _jira_validator is None:
        _jira_validator = JiraKeyValidator()
    return _jira_validator


def validate_jira_key(jira_key: str) -> str:
    """
    Validate a JIRA key using the global validator.

    Args:
        jira_key: The JIRA key to validate

    Returns:
        The validated JIRA key

    Raises:
        JiraKeyValidationError: If validation fails
    """
    validator = get_jira_validator()
    return validator.validate_jira_key(jira_key)
