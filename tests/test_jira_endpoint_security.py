"""Test JIRA key validation in API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.service.main import app


class TestJiraEndpointSecurity:
    """Test JIRA key validation in API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    @pytest.fixture
    def test_container(self, mock_container):
        """Override container with test-specific configuration."""
        # Configure the scroll response for valid JIRA keys
        mock_scroll_result = ([
            MagicMock(payload={
                "uid": "TEST-123",
                "jiraKey": "TEST-123",
                "title": "Test Case",
                "summary": "Test summary",
                "tags": ["test"],
                "priority": "High",
                "testType": "Manual",
                "platforms": [],
                "folderStructure": None,
                "preconditions": [],
                "steps": [],
                "expectedResults": None,
                "testData": None,
                "relatedIssues": [],
                "testPath": None,
                "source": "functional_tests_xray.json",
                "description": None,
                "testCaseId": None
            })
        ], None)

        # Update the mock qdrant client in the container
        mock_qdrant_client = mock_container.get('qdrant_client')
        mock_qdrant_client.scroll.return_value = mock_scroll_result

        # Replace the mock JIRA validator with the real one for security testing
        from src.security.jira_validator import validate_jira_key
        mock_container._instances['jira_validator'] = validate_jira_key

        return mock_container

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_get_by_jira_valid_key(self, client, test_container):
        """Test get by JIRA endpoint with valid JIRA key."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Set up the app state container for testing
            client.app.state.container = test_container

            headers = {"X-API-Key": "test-key"}

            response = client.get("/by-jira/TEST-123", headers=headers)

            assert response.status_code == 200
            data = response.json()
            assert data["jiraKey"] == "TEST-123"

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_get_by_jira_invalid_format(self, client, test_container):
        """Test get by JIRA endpoint with invalid JIRA key format."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Ensure container attribute exists and mock it
            if not hasattr(client.app.state, 'container'):
                client.app.state.container = test_container
            
            with patch.object(client.app.state, 'container', test_container):
                headers = {"X-API-Key": "test-key"}

                invalid_keys = [
                    "test-123",         # Lowercase
                    "TEST-123'",        # SQL injection attempt
                    "TEST-123<script>", # XSS attempt
                    "TEST;DROP TABLE",  # SQL injection
                    "TEST-0",           # Invalid number format
                    "TOOLONGPROJECT-123", # Too long project
                ]

                for invalid_key in invalid_keys:
                    response = client.get(f"/by-jira/{invalid_key}", headers=headers)

                    assert response.status_code == 400
                    assert "Invalid JIRA key format" in response.json()["detail"]

                # Test path traversal separately - may be blocked by FastAPI routing (404) or our validation (400)
                path_traversal_response = client.get("/by-jira/../etc/passwd", headers=headers)
                assert path_traversal_response.status_code in [400, 404]  # Either is good security

                # Test empty string separately (may result in 404 instead of 400)
                empty_response = client.get("/by-jira/", headers=headers)
                assert empty_response.status_code in [400, 404]  # Either is acceptable

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_find_similar_valid_key(self, client, test_container):
        """Test find similar endpoint with valid JIRA key."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the app state to use our test container
            with patch.object(client.app.state, 'container', test_container):
                # Mock search function to avoid complex search logic
                with patch('src.service.main._search_impl') as mock_search:
                    mock_search.return_value = []

                    headers = {"X-API-Key": "test-key"}

                    response = client.get("/similar/PROJECT-456?top_k=5", headers=headers)

                    assert response.status_code == 200

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_find_similar_invalid_format(self, client, test_container):
        """Test find similar endpoint with invalid JIRA key format."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the app state to use our test container
            with patch.object(client.app.state, 'container', test_container):
                headers = {"X-API-Key": "test-key"}

                dangerous_keys = [
                    "project-123",      # Lowercase
                    "PROJ-123|cat",     # Command injection
                    "PROJ-123&wget",    # Command injection
                    "PROJ-123'OR'1=1",  # SQL injection
                    "PROJ<script>",     # XSS
                ]

                for dangerous_key in dangerous_keys:
                    response = client.get(f"/similar/{dangerous_key}", headers=headers)

                    assert response.status_code == 400
                    assert "Invalid JIRA key format" in response.json()["detail"]

                # Note: CRLF injection test skipped as HTTP client blocks control characters in URLs
                # This is actually good security - the transport layer provides additional protection

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_jira_endpoints_require_authentication(self, client, mock_qdrant_client):
        """Test that JIRA endpoints require authentication."""
        # Test without API key
        response = client.get("/by-jira/TEST-123")
        assert response.status_code == 401

        response = client.get("/similar/TEST-123")
        assert response.status_code == 401

    @patch('src.auth.secure_key_manager._key_manager', None)
    @patch('src.service.main.logger')
    def test_security_violations_logged(self, mock_logger, client, mock_qdrant_client):
        """Test that security violations are properly logged."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            headers = {"X-API-Key": "test-key"}

            # Test dangerous JIRA key
            response = client.get("/by-jira/TEST-123';DROP TABLE tests;--", headers=headers)

            assert response.status_code == 400

            # Verify security logging occurred
            mock_logger.error.assert_called()
            call_args = mock_logger.error.call_args
            assert "JIRA key validation failed" in call_args[0][0]
            assert call_args[1]["extra"]["security_event"] is True

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_nonexistent_jira_key_returns_404(self, client, mock_container):
        """Test that nonexistent JIRA keys return 404."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Replace the mock JIRA validator with the real one for this test
            from src.security.jira_validator import validate_jira_key
            mock_container._instances['jira_validator'] = validate_jira_key

            # Configure mock container with empty scroll response
            mock_qdrant_client = mock_container.get('qdrant_client')
            mock_qdrant_client.scroll.return_value = ([], None)

            # Set up the app state container for testing
            client.app.state.container = mock_container

            headers = {"X-API-Key": "test-key"}

            response = client.get("/by-jira/VALID-404", headers=headers)

            assert response.status_code == 404
            assert "Test not found: VALID-404" in response.json()["detail"]

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_jira_key_url_encoding_handled(self, client, mock_container):
        """Test that URL-encoded JIRA keys are handled properly."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Replace the mock JIRA validator with the real one for this test
            from src.security.jira_validator import validate_jira_key
            mock_container._instances['jira_validator'] = validate_jira_key

            # Set up the app state container for testing
            client.app.state.container = mock_container

            headers = {"X-API-Key": "test-key"}

            # Test URL encoded characters (should still be rejected if dangerous)
            response = client.get("/by-jira/TEST%2D123%27", headers=headers)  # TEST-123'

            # The URL decoding happens before our validation, so this should fail
            assert response.status_code == 400

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_jira_key_length_limits_enforced(self, client, mock_container):
        """Test that JIRA key length limits are enforced."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Replace the mock JIRA validator with the real one for this test
            from src.security.jira_validator import validate_jira_key
            mock_container._instances['jira_validator'] = validate_jira_key

            # Set up the app state container for testing
            client.app.state.container = mock_container

            headers = {"X-API-Key": "test-key"}

            # Test overly long JIRA key (triggers regex validation before length check)
            long_key = "A" * 15 + "-123"  # Project key exceeds 10 chars
            response = client.get(f"/by-jira/{long_key}", headers=headers)

            assert response.status_code == 400
            assert "Invalid JIRA key format" in response.json()["detail"]

            # Test key that triggers actual length check (format valid but too long overall)
            very_long_key = "A" * 25 + "-123"  # Far exceeds 20 char MAX_LENGTH
            response = client.get(f"/by-jira/{very_long_key}", headers=headers)

            assert response.status_code == 400
            assert "too long" in response.json()["detail"]

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_jira_key_boundary_conditions(self, client, mock_container):
        """Test JIRA key boundary conditions."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Replace the mock JIRA validator with the real one for this test
            from src.security.jira_validator import validate_jira_key
            mock_container._instances['jira_validator'] = validate_jira_key

            # Set up the app state container for testing
            client.app.state.container = mock_container

            headers = {"X-API-Key": "test-key"}

            # Test minimum valid key (format valid but doesn't exist in mock data)
            response = client.get("/by-jira/AB-1", headers=headers)
            assert response.status_code == 404  # Valid format, but test not found

            # Test maximum valid key (within limits, format valid but doesn't exist in mock data)
            max_project = "A" * 10
            max_key = f"{max_project}-12345678"  # Max 8 digits
            response = client.get(f"/by-jira/{max_key}", headers=headers)
            assert response.status_code == 404  # Valid format, but test not found

            # Test just over the limit
            over_limit_project = "A" * 11  # 11 chars - too long
            response = client.get(f"/by-jira/{over_limit_project}-1", headers=headers)
            assert response.status_code == 400  # Should fail
