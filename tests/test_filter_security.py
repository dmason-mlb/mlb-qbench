"""Security tests for filter input validation and sanitization."""

import pytest
from typing import Dict, Any
from unittest.mock import patch

from src.models.test_models import SearchRequest
from src.models.filter_models import (
    FilterableField,
    FilterOperator, 
    FilterValue,
    ValidatedFilters,
    validate_and_sanitize_filters,
    validate_priority_value,
    validate_test_type_value,
    validate_platform_values
)
from src.service.main import build_filter


class TestFilterValueValidation:
    """Test individual filter value validation."""
    
    def test_valid_string_filter(self):
        """Test valid string filter value."""
        filter_val = FilterValue(
            field=FilterableField.TEST_TYPE,
            operator=FilterOperator.EQUALS,
            value="Functional"
        )
        assert filter_val.value == "Functional"
        assert filter_val.field == FilterableField.TEST_TYPE
    
    def test_empty_string_filter_rejected(self):
        """Test that empty string filter values are rejected."""
        with pytest.raises(ValueError, match="Filter value cannot be empty"):
            FilterValue(
                field=FilterableField.TEST_TYPE,
                operator=FilterOperator.EQUALS,
                value=""
            )
    
    def test_long_string_filter_rejected(self):
        """Test that overly long string filter values are rejected."""
        long_value = "a" * 101  # Exceeds 100 char limit
        with pytest.raises(ValueError, match="Filter value too long"):
            FilterValue(
                field=FilterableField.TEST_TYPE,
                operator=FilterOperator.EQUALS,
                value=long_value
            )
    
    def test_dangerous_characters_rejected(self):
        """Test that potentially dangerous characters are rejected."""
        dangerous_values = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE tests; --",
            "value with 'quotes",
            'value with "quotes',
            "value & ampersand"
        ]
        
        for dangerous_value in dangerous_values:
            with pytest.raises(ValueError, match="dangerous characters"):
                FilterValue(
                    field=FilterableField.TEST_TYPE,
                    operator=FilterOperator.EQUALS,
                    value=dangerous_value
                )
    
    def test_integer_filter_validation(self):
        """Test integer filter value validation."""
        # Valid integer - using a string field that accepts ints
        filter_val = FilterValue(
            field=FilterableField.TEST_TYPE,
            operator=FilterOperator.EQUALS,
            value=1
        )
        assert filter_val.value == 1
        
        # Out of range integer
        with pytest.raises(ValueError, match="out of range"):
            FilterValue(
                field=FilterableField.TEST_TYPE,
                operator=FilterOperator.EQUALS,
                value=2000000
            )
    
    def test_list_filter_validation(self):
        """Test list filter value validation."""
        # Valid list
        filter_val = FilterValue(
            field=FilterableField.PLATFORMS,
            operator=FilterOperator.IN,
            value=["web", "mobile"]
        )
        assert filter_val.value == ["web", "mobile"]
        
        # Empty list
        with pytest.raises(ValueError, match="Filter list cannot be empty"):
            FilterValue(
                field=FilterableField.PLATFORMS,
                operator=FilterOperator.IN,
                value=[]
            )
        
        # Too long list
        long_list = ["item"] * 51
        with pytest.raises(ValueError, match="Filter list too long"):
            FilterValue(
                field=FilterableField.PLATFORMS,
                operator=FilterOperator.IN,
                value=long_list
            )
    
    def test_jira_key_format_validation(self):
        """Test JIRA key format validation."""
        # Valid JIRA keys
        valid_keys = ["TEST-123", "PROJ-1", "FRAMED-1390", "API-001"]
        for key in valid_keys:
            filter_val = FilterValue(
                field=FilterableField.JIRA_KEY,
                operator=FilterOperator.EQUALS,
                value=key
            )
            assert filter_val.value == key
        
        # Invalid JIRA keys
        invalid_keys = ["test-123", "123-TEST", "TEST_123", "TEST-", "-123"]
        for key in invalid_keys:
            with pytest.raises(ValueError, match="Invalid JIRA key format"):
                FilterValue(
                    field=FilterableField.JIRA_KEY,
                    operator=FilterOperator.EQUALS,
                    value=key
                )


class TestValidatedFilters:
    """Test validated filters container."""
    
    def test_too_many_filters_rejected(self):
        """Test that too many filters are rejected for DoS protection."""
        filters = []
        for i in range(21):  # Exceeds limit of 20
            filters.append(FilterValue(
                field=FilterableField.TEST_TYPE,
                operator=FilterOperator.EQUALS,
                value="Functional"
            ))
        
        with pytest.raises(ValueError, match="Too many filters"):
            ValidatedFilters(filters=filters)
    
    def test_to_qdrant_filter_dict(self):
        """Test conversion to Qdrant filter dictionary."""
        filters = [
            FilterValue(
                field=FilterableField.TEST_TYPE,
                operator=FilterOperator.EQUALS,
                value="Functional"
            ),
            FilterValue(
                field=FilterableField.PLATFORMS,
                operator=FilterOperator.IN,
                value=["web", "mobile"]
            )
        ]
        
        validated = ValidatedFilters(filters=filters)
        result = validated.to_qdrant_filter_dict()
        
        assert result is not None
        assert result["testType"] == "Functional"
        assert result["platforms"] == ["web", "mobile"]


class TestFilterSanitization:
    """Test the main filter sanitization function."""
    
    def test_valid_filters_pass(self):
        """Test that valid filters pass sanitization."""
        filters = {
            "testType": "Functional",
            "priority": "High",
            "platforms": ["web", "mobile"]
        }
        
        result = validate_and_sanitize_filters(filters)
        
        assert result is not None
        assert result["testType"] == "Functional"
        assert result["priority"] == "High"
        assert result["platforms"] == ["web", "mobile"]
    
    def test_invalid_field_rejected(self):
        """Test that invalid fields are rejected."""
        filters = {
            "malicious_field": "value",
            "testType": "Functional"
        }
        
        with pytest.raises(ValueError, match="Invalid filter field"):
            validate_and_sanitize_filters(filters)
    
    def test_empty_filters_return_none(self):
        """Test that empty filters return None."""
        assert validate_and_sanitize_filters(None) is None
        assert validate_and_sanitize_filters({}) is None
    
    def test_contains_operator_handling(self):
        """Test that contains operator is handled correctly."""
        filters = {
            "folderStructure__contains": "API"
        }
        
        result = validate_and_sanitize_filters(filters)
        
        assert result is not None
        assert "folderStructure__contains" in result


class TestBuildFilterSecurity:
    """Test the build_filter function security."""
    
    def test_build_filter_with_valid_input(self):
        """Test build_filter with valid input."""
        filters = {
            "testType": "Functional",
            "platforms": ["web"]
        }
        
        result = build_filter(filters)
        
        assert result is not None
        assert len(result.must) == 2
    
    def test_build_filter_with_invalid_input_raises_error(self):
        """Test that build_filter raises error for invalid input."""
        filters = {
            "malicious_field": "<script>alert('xss')</script>"
        }
        
        with pytest.raises(ValueError, match="Invalid filter parameters"):
            build_filter(filters)
    
    @patch('src.service.main.logger')
    def test_build_filter_logs_security_violations(self, mock_logger):
        """Test that security violations are logged."""
        filters = {
            "malicious_field": "dangerous_value"
        }
        
        with pytest.raises(ValueError):
            build_filter(filters)
        
        # Verify security event was logged
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert "security threat" in call_args[0][0]
        assert call_args[1]["extra"]["security_event"] is True
    
    def test_build_filter_with_none_returns_none(self):
        """Test that build_filter returns None for None input."""
        assert build_filter(None) is None


class TestSearchRequestValidation:
    """Test search request query validation."""
    
    def test_dangerous_query_characters_rejected(self):
        """Test that dangerous characters in search query are rejected."""
        
        dangerous_queries = [
            "<script>alert('xss')</script>",
            "query with 'quotes",
            'query with "quotes',
            "query & ampersand"
        ]
        
        for query in dangerous_queries:
            with pytest.raises(ValueError, match="dangerous characters"):
                SearchRequest(
                    query=query,
                    top_k=10
                )
    
    def test_sql_injection_patterns_rejected(self):
        """Test that SQL injection patterns are rejected."""
        
        sql_queries = [
            "test UNION SELECT * FROM users",
            "test'; DROP TABLE tests; --",  
            "test /* comment */ SELECT",
            "test query INSERT INTO"
        ]
        
        for query in sql_queries:
            with pytest.raises(ValueError, match="(dangerous characters|dangerous SQL patterns)"):
                SearchRequest(
                    query=query,
                    top_k=10
                )
    
    def test_valid_query_passes(self):
        """Test that valid queries pass validation."""
        valid_queries = [
            "login functionality test",
            "API authentication flow",
            "user registration process",
            "payment gateway integration"
        ]
        
        for query in valid_queries:
            request = SearchRequest(
                query=query,
                top_k=10
            )
            assert request.query == query.strip()


class TestValueValidationHelpers:
    """Test specific value validation helpers."""
    
    def test_priority_validation(self):
        """Test priority value validation."""
        valid_priorities = ["Critical", "High", "Medium", "Low"]
        for priority in valid_priorities:
            assert validate_priority_value(priority) == priority
        
        with pytest.raises(ValueError, match="Invalid priority"):
            validate_priority_value("Invalid")
    
    def test_test_type_validation(self):
        """Test test type value validation."""
        valid_types = ["Functional", "API", "Integration", "Unit", "Performance"]
        for test_type in valid_types:
            assert validate_test_type_value(test_type) == test_type
        
        with pytest.raises(ValueError, match="Invalid test type"):
            validate_test_type_value("Invalid")
    
    def test_platform_validation(self):
        """Test platform values validation."""
        valid_platforms = ["web", "mobile", "api", "desktop"]
        assert validate_platform_values(valid_platforms) == valid_platforms
        
        with pytest.raises(ValueError, match="Invalid platform"):
            validate_platform_values(["web", "invalid_platform"])