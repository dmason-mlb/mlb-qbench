"""Comprehensive unit tests for core data models.

Tests the TestDoc and TestStep models from src.models.test_models,
covering validation, serialization, field normalization, and edge cases.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.models.test_models import TestDoc, TestStep, SearchRequest, IngestRequest, UpdateJiraKeyRequest


class TestTestStep:
    """Test cases for the TestStep model."""

    def test_valid_test_step_creation(self):
        """Test creating a valid TestStep with all required fields."""
        step = TestStep(
            index=1,
            action="Click the login button",
            expected=["Login form appears", "Form is focusable"]
        )
        
        assert step.index == 1
        assert step.action == "Click the login button"
        assert step.expected == ["Login form appears", "Form is focusable"]

    def test_test_step_minimal_fields(self):
        """Test creating TestStep with only required fields."""
        step = TestStep(
            index=1,
            action="Navigate to home page"
        )
        
        assert step.index == 1
        assert step.action == "Navigate to home page"
        assert step.expected == []  # Should default to empty list

    def test_test_step_index_validation(self):
        """Test that step index must be >= 1."""
        # Valid index
        step = TestStep(index=1, action="Test action")
        assert step.index == 1
        
        # Test edge case - index 1 should be valid
        step = TestStep(index=1, action="Test action")
        assert step.index == 1
        
        # Invalid index - zero
        with pytest.raises(ValidationError) as exc_info:
            TestStep(index=0, action="Test action")
        assert "Step index must be >= 1" in str(exc_info.value)
        
        # Invalid index - negative
        with pytest.raises(ValidationError) as exc_info:
            TestStep(index=-1, action="Test action")
        assert "Step index must be >= 1" in str(exc_info.value)

    def test_test_step_action_required(self):
        """Test that action field is required."""
        # Action field is required by Pydantic, so missing it should fail
        with pytest.raises(ValidationError):
            TestStep(index=1)  # Missing action field

    def test_test_step_expected_list_handling(self):
        """Test that expected field properly handles different input types."""
        # Single string should be converted to list
        step = TestStep(index=1, action="Test", expected=["Result 1", "Result 2"])
        assert isinstance(step.expected, list)
        assert len(step.expected) == 2
        
        # Empty list should be preserved
        step = TestStep(index=1, action="Test", expected=[])
        assert step.expected == []


class TestTestDoc:
    """Test cases for the TestDoc model."""

    def test_valid_test_doc_creation(self):
        """Test creating a valid TestDoc with all fields."""
        test_doc = TestDoc(
            uid="test-12345",
            testCaseId="TC-12345",
            jiraKey="PROJ-123",
            title="Sample Login Test",
            summary="Test user login functionality",
            description="This test verifies that users can log in successfully",
            testType="Manual",
            priority="High",
            platforms=["web", "mobile"],
            tags=["login", "authentication"],
            folderStructure="/Authentication/Login",
            steps=[
                TestStep(index=1, action="Navigate to login", expected=["Login page loads"]),
                TestStep(index=2, action="Enter credentials", expected=["Credentials accepted"])
            ],
            source="functional_tests_xray.json"
        )
        
        assert test_doc.uid == "test-12345"
        assert test_doc.testCaseId == "TC-12345"
        assert test_doc.jiraKey == "PROJ-123"
        assert test_doc.title == "Sample Login Test"
        assert test_doc.testType == "Manual"
        assert test_doc.priority == "High"
        assert len(test_doc.steps) == 2
        assert test_doc.platforms == ["web", "mobile"]
        assert test_doc.tags == ["login", "authentication"]

    def test_test_doc_minimal_required_fields(self):
        """Test creating TestDoc with only required fields."""
        test_doc = TestDoc(
            uid="minimal-test",
            title="Minimal Test",
            source="functional_tests_xray.json"
        )
        
        assert test_doc.uid == "minimal-test"
        assert test_doc.title == "Minimal Test"
        assert test_doc.testType == "Manual"  # Default value
        assert test_doc.priority == "Medium"  # Default value
        assert test_doc.platforms == []  # Default empty list
        assert test_doc.tags == []  # Default empty list
        assert test_doc.steps == []  # Default empty list
        assert isinstance(test_doc.ingested_at, datetime)

    def test_uid_validation(self):
        """Test UID validation rules."""
        # Valid UID
        test_doc = TestDoc(uid="valid-uid", title="Test", source="functional_tests_xray.json")
        assert test_doc.uid == "valid-uid"
        
        # UID with spaces should be trimmed
        test_doc = TestDoc(uid="  spaced-uid  ", title="Test", source="functional_tests_xray.json")
        assert test_doc.uid == "spaced-uid"
        
        # Empty UID should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            TestDoc(uid="", title="Test", source="functional_tests_xray.json")
        assert "uid cannot be empty" in str(exc_info.value)
        
        # Whitespace-only UID should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            TestDoc(uid="   ", title="Test", source="functional_tests_xray.json")
        assert "uid cannot be empty" in str(exc_info.value)
        
        # None UID should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            TestDoc(uid=None, title="Test", source="functional_tests_xray.json")

    def test_list_field_normalization(self):
        """Test that list fields properly normalize different input types."""
        # Test tags normalization
        test_doc = TestDoc(
            uid="test-123",
            title="Test",
            source="functional_tests_xray.json",
            tags="single-tag"  # Single string should become list
        )
        assert test_doc.tags == ["single-tag"]
        
        # Test platforms normalization
        test_doc = TestDoc(
            uid="test-123",
            title="Test", 
            source="functional_tests_xray.json",
            platforms="web"  # Single string should become list
        )
        assert test_doc.platforms == ["web"]
        
        # Test relatedIssues normalization
        test_doc = TestDoc(
            uid="test-123",
            title="Test",
            source="functional_tests_xray.json",
            relatedIssues="ISSUE-123"  # Single string should become list
        )
        assert test_doc.relatedIssues == ["ISSUE-123"]
        
        # Test None values become empty lists
        test_doc = TestDoc(
            uid="test-123",
            title="Test",
            source="functional_tests_xray.json",
            tags=None,
            platforms=None,
            relatedIssues=None
        )
        assert test_doc.tags == []
        assert test_doc.platforms == []
        assert test_doc.relatedIssues == []

    def test_test_type_validation(self):
        """Test that testType accepts only valid literal values."""
        valid_types = ["Manual", "Automated", "API", "Performance", "Integration", "Unit"]
        
        for test_type in valid_types:
            test_doc = TestDoc(
                uid="test-123",
                title="Test",
                source="functional_tests_xray.json",
                testType=test_type
            )
            assert test_doc.testType == test_type
        
        # Invalid test type should raise validation error
        with pytest.raises(ValidationError):
            TestDoc(
                uid="test-123",
                title="Test",
                source="functional_tests_xray.json",
                testType="InvalidType"
            )

    def test_priority_validation(self):
        """Test that priority accepts only valid literal values."""
        valid_priorities = ["Critical", "High", "Medium", "Low"]
        
        for priority in valid_priorities:
            test_doc = TestDoc(
                uid="test-123",
                title="Test",
                source="functional_tests_xray.json",
                priority=priority
            )
            assert test_doc.priority == priority
        
        # Invalid priority should raise validation error
        with pytest.raises(ValidationError):
            TestDoc(
                uid="test-123",
                title="Test",
                source="functional_tests_xray.json",
                priority="InvalidPriority"
            )

    def test_source_validation(self):
        """Test that source accepts only valid literal values."""
        valid_sources = ["functional_tests_xray.json", "api_tests_xray.json"]
        
        for source in valid_sources:
            test_doc = TestDoc(
                uid="test-123",
                title="Test",
                source=source
            )
            assert test_doc.source == source
        
        # Invalid source should raise validation error
        with pytest.raises(ValidationError):
            TestDoc(
                uid="test-123",
                title="Test",
                source="invalid_source.json"
            )

    def test_nested_test_steps(self):
        """Test TestDoc with nested TestStep objects."""
        steps = [
            TestStep(index=1, action="First action", expected=["First result"]),
            TestStep(index=2, action="Second action", expected=["Second result", "Third result"])
        ]
        
        test_doc = TestDoc(
            uid="test-with-steps",
            title="Test with steps",
            source="functional_tests_xray.json",
            steps=steps
        )
        
        assert len(test_doc.steps) == 2
        assert test_doc.steps[0].index == 1
        assert test_doc.steps[0].action == "First action"
        assert test_doc.steps[1].expected == ["Second result", "Third result"]

    def test_ingested_at_auto_generation(self):
        """Test that ingested_at is automatically set."""
        test_doc = TestDoc(
            uid="test-123",
            title="Test",
            source="functional_tests_xray.json"
        )
        
        assert isinstance(test_doc.ingested_at, datetime)
        # Should be recent (within last few seconds)
        time_diff = datetime.utcnow() - test_doc.ingested_at
        assert time_diff.total_seconds() < 10


class TestSearchRequest:
    """Test cases for the SearchRequest model."""

    def test_valid_search_request(self):
        """Test creating a valid search request."""
        request = SearchRequest(
            query="login test authentication",
            top_k=15,
            filters={"priority": "High", "tags": ["web"]},
            scope="all"
        )
        
        assert request.query == "login test authentication"
        assert request.top_k == 15
        assert request.filters == {"priority": "High", "tags": ["web"]}
        assert request.scope == "all"

    def test_search_request_defaults(self):
        """Test SearchRequest with default values."""
        request = SearchRequest(query="test query")
        
        assert request.query == "test query"
        assert request.top_k == 20  # Default value
        assert request.filters is None  # Default value
        assert request.scope == "all"  # Default value

    def test_query_validation_dangerous_characters(self):
        """Test that dangerous characters in query are rejected."""
        dangerous_queries = [
            "<script>alert('xss')</script>",
            "test & echo 'hack'",
            "query with < and >",
            'query with "quotes"',
            "query with 'single quotes'",
        ]
        
        for dangerous_query in dangerous_queries:
            with pytest.raises(ValidationError) as exc_info:
                SearchRequest(query=dangerous_query)
            assert "potentially dangerous characters" in str(exc_info.value)

    def test_query_validation_sql_patterns(self):
        """Test that SQL injection patterns are rejected."""
        sql_queries = [
            "SELECT * FROM tests",
            "UNION SELECT password",
            "INSERT INTO users",
            "DELETE FROM tests", 
            "DROP TABLE users",
            "CREATE TABLE evil",
            "ALTER TABLE tests",
            "test query -- comment",
            "test /* comment */ query",
        ]
        
        for sql_query in sql_queries:
            with pytest.raises(ValidationError) as exc_info:
                SearchRequest(query=sql_query)
            assert "potentially dangerous SQL patterns" in str(exc_info.value)

    def test_query_length_validation(self):
        """Test query length constraints."""
        # Valid length
        request = SearchRequest(query="a" * 100)
        assert len(request.query) == 100
        
        # Empty query should fail
        with pytest.raises(ValidationError):
            SearchRequest(query="")
        
        # Too long query should fail
        with pytest.raises(ValidationError):
            SearchRequest(query="a" * 1001)

    def test_top_k_validation(self):
        """Test top_k parameter validation."""
        # Valid range
        request = SearchRequest(query="test", top_k=50)
        assert request.top_k == 50
        
        # Below minimum should fail
        with pytest.raises(ValidationError):
            SearchRequest(query="test", top_k=0)
        
        # Above maximum should fail
        with pytest.raises(ValidationError):
            SearchRequest(query="test", top_k=101)

    def test_scope_validation(self):
        """Test scope parameter validation."""
        valid_scopes = ["all", "docs", "steps"]
        
        for scope in valid_scopes:
            request = SearchRequest(query="test", scope=scope)
            assert request.scope == scope
        
        # Invalid scope should fail
        with pytest.raises(ValidationError):
            SearchRequest(query="test", scope="invalid")


class TestIngestRequest:
    """Test cases for the IngestRequest model."""

    def test_valid_ingest_request_functional_only(self):
        """Test IngestRequest with only functional path."""
        request = IngestRequest(functional_path="/path/to/functional_tests.json")
        
        assert request.functional_path == "/path/to/functional_tests.json"
        assert request.api_path is None

    def test_valid_ingest_request_api_only(self):
        """Test IngestRequest with only API path."""
        request = IngestRequest(api_path="/path/to/api_tests.json")
        
        assert request.api_path == "/path/to/api_tests.json"
        assert request.functional_path is None

    def test_valid_ingest_request_both_paths(self):
        """Test IngestRequest with both paths."""
        request = IngestRequest(
            functional_path="/path/to/functional_tests.json",
            api_path="/path/to/api_tests.json"
        )
        
        assert request.functional_path == "/path/to/functional_tests.json"
        assert request.api_path == "/path/to/api_tests.json"

    def test_ingest_request_no_paths_validation(self):
        """Test that at least one path must be provided."""
        # No paths should fail validation
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest()
        assert "At least one path must be provided" in str(exc_info.value)
        
        # Empty strings should also fail
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest(functional_path="", api_path="")
        assert "At least one path must be provided" in str(exc_info.value)
        
        # None values should fail
        with pytest.raises(ValidationError) as exc_info:
            IngestRequest(functional_path=None, api_path=None)
        assert "At least one path must be provided" in str(exc_info.value)


class TestUpdateJiraKeyRequest:
    """Test cases for the UpdateJiraKeyRequest model."""

    def test_valid_jira_key_formats(self):
        """Test various valid JIRA key formats."""
        valid_keys = [
            "PROJECT-123",
            "DEV-456", 
            "TEST-1",
            "ABCD-999",
            "AB-1",  # Minimum 2 chars before hyphen
            "PROJECT123-456",
            "ABC123-999"
        ]
        
        for jira_key in valid_keys:
            request = UpdateJiraKeyRequest(jiraKey=jira_key)
            assert request.jiraKey == jira_key.upper()  # Should be normalized to uppercase

    def test_jira_key_normalization(self):
        """Test that JIRA keys are normalized to uppercase."""
        request = UpdateJiraKeyRequest(jiraKey="project-123")
        assert request.jiraKey == "PROJECT-123"
        
        request = UpdateJiraKeyRequest(jiraKey="  dev-456  ")
        assert request.jiraKey == "DEV-456"  # Should also trim whitespace

    def test_invalid_jira_key_formats(self):
        """Test that invalid JIRA key formats are rejected."""
        invalid_keys = [
            "PROJECT_123",  # underscore instead of hyphen
            "-123",  # missing project part
            "PROJECT-",  # missing number part
            "PROJECT",  # missing hyphen and number
            "123-PROJECT",  # number first
            "PROJECT-123-EXTRA",  # too many parts
            "PR OJECT-123",  # space in project name
            "PROJECT-12.3",  # decimal in number
            "A-123",  # only one character before hyphen (minimum is 2)
        ]
        
        for invalid_key in invalid_keys:
            with pytest.raises(ValidationError) as exc_info:
                UpdateJiraKeyRequest(jiraKey=invalid_key)
            assert "Invalid JIRA key format" in str(exc_info.value)
        
        # Test empty string separately as it triggers min_length validation first
        with pytest.raises(ValidationError) as exc_info:
            UpdateJiraKeyRequest(jiraKey="")
        # Empty string triggers Pydantic's min_length constraint, not our custom validator
        assert "String should have at least 1 character" in str(exc_info.value)

    def test_jira_key_length_validation(self):
        """Test JIRA key length constraints."""
        # Valid minimum length (needs at least 2 chars before hyphen)
        request = UpdateJiraKeyRequest(jiraKey="AB-1")
        assert request.jiraKey == "AB-1"
        
        # Minimum length (empty should fail due to pattern)
        with pytest.raises(ValidationError):
            UpdateJiraKeyRequest(jiraKey="")
        
        # Maximum length (should pass if format is valid)
        long_key = "A" * 45 + "-123"  # 49 characters, should pass
        request = UpdateJiraKeyRequest(jiraKey=long_key)
        assert request.jiraKey == long_key
        
        # Too long should fail
        with pytest.raises(ValidationError):
            UpdateJiraKeyRequest(jiraKey="A" * 60 + "-123")  # Over 50 chars


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_test_doc_json_serialization(self):
        """Test that TestDoc can be serialized to and from JSON."""
        test_doc = TestDoc(
            uid="test-123",
            title="Test Document",
            source="functional_tests_xray.json",
            testType="Manual",
            priority="High",
            tags=["web", "auth"],
            steps=[
                TestStep(index=1, action="Login", expected=["Success"])
            ]
        )
        
        # Serialize to dict
        doc_dict = test_doc.model_dump()
        assert isinstance(doc_dict, dict)
        assert doc_dict["uid"] == "test-123"
        assert doc_dict["title"] == "Test Document"
        assert len(doc_dict["steps"]) == 1
        
        # Deserialize from dict
        new_doc = TestDoc.model_validate(doc_dict)
        assert new_doc.uid == test_doc.uid
        assert new_doc.title == test_doc.title
        assert len(new_doc.steps) == 1
        assert new_doc.steps[0].action == "Login"

    def test_test_step_json_serialization(self):
        """Test that TestStep can be serialized to and from JSON."""
        step = TestStep(
            index=1,
            action="Click button",
            expected=["Button clicked", "Page changes"]
        )
        
        # Serialize to dict
        step_dict = step.model_dump()
        assert isinstance(step_dict, dict)
        assert step_dict["index"] == 1
        assert step_dict["action"] == "Click button"
        assert step_dict["expected"] == ["Button clicked", "Page changes"]
        
        # Deserialize from dict
        new_step = TestStep.model_validate(step_dict)
        assert new_step.index == step.index
        assert new_step.action == step.action
        assert new_step.expected == step.expected