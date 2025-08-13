"""Test JIRA key validation to prevent injection attacks."""

from unittest.mock import patch

import pytest

from src.security.jira_validator import JiraKeyValidationError, JiraKeyValidator, validate_jira_key


class TestJiraKeyValidator:
    """Test the JIRA key validator."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        return JiraKeyValidator()

    def test_valid_jira_keys(self, validator):
        """Test validation of valid JIRA keys."""
        valid_keys = [
            "ABC-123",          # Standard format
            "PROJ-456",         # Different project
            "TEST-1",           # Single digit
            "DEV-99999999",     # Max digits (8)
            "A1-1",             # Min project length (2)
            "PROJECT123-1",     # Project with numbers
            "Z9ABC8DEF7-123456", # Max project length (10)
        ]

        for key in valid_keys:
            result = validator.validate_jira_key(key)
            assert result == key

    def test_empty_jira_key(self, validator):
        """Test rejection of empty JIRA keys."""
        with pytest.raises(JiraKeyValidationError, match="cannot be empty"):
            validator.validate_jira_key("")

        with pytest.raises(JiraKeyValidationError, match="cannot be empty"):
            validator.validate_jira_key(None)

    def test_jira_key_too_long(self, validator):
        """Test rejection of JIRA keys that are too long."""
        # First test - exceeds MAX_LENGTH check (should trigger length error before format)
        very_long_key = "A" * 25 + "-123"  # Far exceeds MAX_LENGTH of 20
        with pytest.raises(JiraKeyValidationError, match="too long"):
            validator.validate_jira_key(very_long_key)

        # Second test - project key too long but total length OK (format error)
        long_project_key = "A" * 15 + "-123"  # Project exceeds 10 chars but total < 20
        with pytest.raises(JiraKeyValidationError, match="Invalid JIRA key format"):
            validator.validate_jira_key(long_project_key)

    def test_dangerous_characters_rejected(self, validator):
        """Test rejection of JIRA keys with dangerous characters."""
        dangerous_keys = [
            "ABC-123'",         # SQL injection
            'ABC-123"',         # SQL injection
            "ABC-123<script>",  # XSS
            "ABC-123>",         # XSS
            "ABC-123&cmd",      # Command injection
            "ABC-123|cat",      # Command injection
            "ABC-123;rm",       # Command injection
            "ABC-123()",        # Command injection
            "ABC-123{}",        # Command injection
            "ABC-123[]",        # Command injection
            "ABC-123\\",        # Path traversal
            "ABC-123/",         # Path traversal
            "ABC-123?",         # URL manipulation
            "ABC-123#",         # URL fragment
            "ABC-123%20",       # URL encoding
            "ABC-123\n",        # CRLF injection
            "ABC-123\r",        # CRLF injection
            "ABC-123\t",        # Tab character
            "ABC-123\x00",      # Null byte
        ]

        for key in dangerous_keys:
            with pytest.raises(JiraKeyValidationError, match="invalid character"):
                validator.validate_jira_key(key)

    def test_invalid_format_rejected(self, validator):
        """Test rejection of JIRA keys with invalid format."""
        invalid_keys = [
            "abc-123",          # Lowercase project
            "ABC",              # Missing hyphen and number
            "ABC-",             # Missing number
            "-123",             # Missing project
            "A-123",            # Project too short (1 char)
            "ABCDEFGHIJK-123",  # Project too long (11 chars)
            "ABC-0",            # Number starts with 0
            "ABC-123456789",    # Number too long (9 digits)
            "ABC-12A",          # Non-numeric issue number
            "ABC_123",          # Underscore instead of hyphen
            "ABC 123",          # Space instead of hyphen
            "123-ABC",          # Reversed format
        ]

        for key in invalid_keys:
            with pytest.raises(JiraKeyValidationError, match="Invalid JIRA key format"):
                validator.validate_jira_key(key)

    def test_project_key_too_short(self, validator):
        """Test rejection of project keys that are too short."""
        with pytest.raises(JiraKeyValidationError, match="Invalid JIRA key format"):
            validator.validate_jira_key("A-123")

    def test_is_valid_jira_key_format(self, validator):
        """Test the format checking method."""
        assert validator.is_valid_jira_key_format("ABC-123") is True
        assert validator.is_valid_jira_key_format("abc-123") is False
        assert validator.is_valid_jira_key_format("ABC-123'") is False
        assert validator.is_valid_jira_key_format("") is False

    @patch('src.security.jira_validator.logger')
    def test_security_events_logged(self, mock_logger, validator):
        """Test that security violations are logged."""
        # Test dangerous character logging
        with pytest.raises(JiraKeyValidationError):
            validator.validate_jira_key("ABC-123'")

        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args
        assert "Dangerous character in JIRA key" in call_args[0][0]
        assert call_args[1]["extra"]["security_event"] is True

        # Test format validation logging
        mock_logger.reset_mock()
        with pytest.raises(JiraKeyValidationError):
            validator.validate_jira_key("abc-123")

        mock_logger.warning.assert_called()
        call_args = mock_logger.warning.call_args
        assert "Invalid JIRA key format" in call_args[0][0]
        assert call_args[1]["extra"]["security_event"] is True

    @patch('src.security.jira_validator.logger')
    def test_successful_validation_logged(self, mock_logger, validator):
        """Test that successful validations are logged."""
        result = validator.validate_jira_key("ABC-123")
        assert result == "ABC-123"

        mock_logger.debug.assert_called()
        call_args = mock_logger.debug.call_args
        assert "JIRA key validation successful" in call_args[0][0]
        assert call_args[1]["key"] == "ABC-123"
        assert call_args[1]["project"] == "ABC"


class TestGlobalValidator:
    """Test the global validator functions."""

    def test_validate_jira_key_function(self):
        """Test the global validate_jira_key function."""
        result = validate_jira_key("TEST-456")
        assert result == "TEST-456"

    def test_validate_jira_key_function_error(self):
        """Test the global validate_jira_key function with invalid input."""
        with pytest.raises(JiraKeyValidationError):
            validate_jira_key("invalid")

    def test_global_validator_singleton(self):
        """Test that the global validator is a singleton."""
        from src.security.jira_validator import get_jira_validator

        validator1 = get_jira_validator()
        validator2 = get_jira_validator()

        assert validator1 is validator2


class TestJiraKeyEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance for testing."""
        return JiraKeyValidator()

    def test_boundary_lengths(self, validator):
        """Test boundary conditions for lengths."""
        # Minimum valid lengths
        assert validator.validate_jira_key("AB-1") == "AB-1"

        # Maximum valid lengths
        max_project = "A" * 10  # 10 chars is max
        max_number = "1" + "0" * 7  # 8 digits max
        max_key = f"{max_project}-{max_number}"
        assert validator.validate_jira_key(max_key) == max_key

        # Just over the limits should fail
        over_project = "A" * 11  # 11 chars
        with pytest.raises(JiraKeyValidationError):
            validator.validate_jira_key(f"{over_project}-1")

        over_number = "1" + "0" * 8  # 9 digits
        with pytest.raises(JiraKeyValidationError):
            validator.validate_jira_key(f"AB-{over_number}")

    def test_special_valid_combinations(self, validator):
        """Test special but valid combinations."""
        valid_special = [
            "A2-1",             # Single letter + number in project
            "AB2C3-99",         # Mixed alphanumeric project
            "TEST123-1234567",  # Max length combinations
        ]

        for key in valid_special:
            assert validator.validate_jira_key(key) == key

    def test_unicode_and_special_encoding(self, validator):
        """Test handling of unicode and special encoding."""
        unicode_keys = [
            "ABΓ-123",          # Greek letter
            "AB€-123",          # Euro symbol
            "AB\u00A0-123",     # Non-breaking space
            "AB\u2013-123",     # En dash (looks like hyphen)
        ]

        for key in unicode_keys:
            with pytest.raises(JiraKeyValidationError):
                validator.validate_jira_key(key)
