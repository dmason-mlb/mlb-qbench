"""Tests for the normalization module."""

import pytest
from datetime import datetime
from src.ingest.normalize import (
    normalize_functional_test,
    normalize_api_test,
    normalize_priority
)


class TestFunctionalNormalization:
    """Test functional test normalization."""
    
    def test_functional_test_with_issuekey_mapping(self):
        """Test that issueKey is correctly mapped to jiraKey."""
        raw_data = {
            "issueKey": "FRAMED-1390",
            "testCaseId": "tc_func_1390",
            "summary": "Test Summary",
            "labels": ["tag1", "tag2"],
            "priority": "High",
            "folder": "/Web/Team",
            "platforms": ["web"],
            "testScript": {
                "steps": [
                    {
                        "index": 1,
                        "action": "Do something",
                        "result": "Something happens"
                    }
                ]
            }
        }
        
        result = normalize_functional_test(raw_data)
        
        assert result is not None
        assert result.jiraKey == "FRAMED-1390"
        assert result.testCaseId == "tc_func_1390"
        assert result.uid == "FRAMED-1390"
        assert result.title == "Test Summary"
        assert result.tags == ["tag1", "tag2"]
        assert len(result.steps) == 1
        assert result.steps[0].expected == ["Something happens"]
    
    def test_functional_test_without_testinfo(self):
        """Test normalization when testInfo is missing (flattened structure)."""
        raw_data = {
            "issueKey": "FRAMED-1391",
            "testCaseId": "tc_func_1391",
            "summary": "Flattened Test",
            "labels": ["tag1"],
            "priority": "Medium",
            "folder": "/API/Test",
            "platforms": ["api"],
            "testScript": {
                "steps": [
                    {"action": "Call API", "result": "200 OK"}
                ]
            }
        }
        
        result = normalize_functional_test(raw_data)
        
        assert result is not None
        assert result.jiraKey == "FRAMED-1391"
        assert result.title == "Flattened Test"
        assert result.folderStructure == "/API/Test"
        assert result.platforms == ["api"]
    
    def test_functional_test_with_nested_rows(self):
        """Test that nested rows structure is rejected."""
        raw_data = {
            "rows": [
                {"issueKey": "FRAMED-1", "summary": "Test 1"},
                {"issueKey": "FRAMED-2", "summary": "Test 2"}
            ]
        }
        
        result = normalize_functional_test(raw_data)
        assert result is None


class TestAPINormalization:
    """Test API test normalization."""
    
    def test_api_test_lowercase_testtype(self):
        """Test that lowercase 'api' testType is converted to uppercase."""
        raw_data = {
            "jiraKey": "API-001",
            "testCaseId": "tc_api_001",
            "title": "API Test",
            "testType": "api",  # lowercase
            "priority": "High",
            "platforms": ["web"],
            "folderStructure": "API/Tests",
            "tags": ["api", "test"],
            "steps": [
                {"action": "Send request", "expected": ["200 OK"]}
            ]
        }
        
        result = normalize_api_test(raw_data)
        
        assert result is not None
        assert result.testType == "API"  # Should be uppercase
    
    def test_api_test_folderstructure_list(self):
        """Test that folderStructure list is converted to string path."""
        raw_data = {
            "jiraKey": "API-002",
            "testCaseId": "tc_api_002",
            "title": "API Test with List Folder",
            "priority": "Medium",
            "folderStructure": ["API", "Team", "Roster"],  # List format
            "tags": ["api"],
            "steps": []
        }
        
        result = normalize_api_test(raw_data)
        
        assert result is not None
        assert result.folderStructure == "API/Team/Roster"  # Should be joined with /
    
    def test_api_test_with_summary(self):
        """Test that summary field is used when present."""
        raw_data = {
            "jiraKey": "API-003",
            "title": "Title Text",
            "summary": "Summary Text",
            "priority": "Low",
            "folderStructure": "API",
            "tags": []
        }
        
        result = normalize_api_test(raw_data)
        
        assert result is not None
        assert result.summary == "Summary Text"
        assert result.title == "Title Text"
    
    def test_api_test_null_jirakey(self):
        """Test handling of null jiraKey with fallback to testCaseId."""
        raw_data = {
            "jiraKey": None,
            "testCaseId": "tc_api_004",
            "title": "Test with null jiraKey",
            "priority": "High",
            "folderStructure": "API/Null",
            "tags": ["null-test"]
        }
        
        result = normalize_api_test(raw_data)
        
        assert result is not None
        assert result.uid == "tc_api_004"
        assert result.jiraKey is None
        assert result.testCaseId == "tc_api_004"


class TestPriorityNormalization:
    """Test priority normalization."""
    
    def test_priority_normalization(self):
        """Test various priority formats are normalized correctly."""
        assert normalize_priority("high") == "High"
        assert normalize_priority("HIGH") == "High"
        assert normalize_priority("1") == "Critical"
        assert normalize_priority("p2") == "High"
        assert normalize_priority("") == "Medium"
        assert normalize_priority(None) == "Medium"
        assert normalize_priority("unknown") == "Medium"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])