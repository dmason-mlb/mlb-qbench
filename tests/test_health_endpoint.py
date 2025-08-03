"""Test health endpoint authentication."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.service.main import app


class TestHealthEndpoint:
    """Test health endpoint security."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_health_endpoint_requires_authentication(self, client):
        """Test that health endpoint requires API key."""
        response = client.get("/healthz")
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Missing API key"
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    @patch.dict('os.environ', {"MASTER_API_KEY": "test-master-key"}, clear=True)
    @patch('src.service.main.check_collections_health')
    def test_health_endpoint_with_valid_key(self, mock_health_check, client):
        """Test health endpoint with valid API key."""
        # Clear global key manager to force reload
        from src.auth import secure_key_manager
        secure_key_manager._key_manager = None
        
        # Mock healthy status
        mock_health_check.return_value = {
            "status": "healthy",
            "collections": {
                "test_docs": {"count": 100},
                "test_steps": {"count": 500}
            }
        }
        
        headers = {"X-API-Key": "test-master-key"}
        response = client.get("/healthz", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "qdrant" in data
        
        # Verify health check was called
        mock_health_check.assert_called_once()
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    @patch.dict('os.environ', {"MASTER_API_KEY": "test-master-key"}, clear=True)
    @patch('src.service.main.check_collections_health')
    def test_health_endpoint_with_degraded_status(self, mock_health_check, client):
        """Test health endpoint with degraded status."""
        # Clear global key manager to force reload
        from src.auth import secure_key_manager
        secure_key_manager._key_manager = None
        
        # Mock degraded status
        mock_health_check.return_value = {
            "status": "degraded",
            "collections": {
                "test_docs": {"count": 100},
                "test_steps": {"count": 0}  # Missing steps
            }
        }
        
        headers = {"X-API-Key": "test-master-key"}
        response = client.get("/healthz", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["qdrant"]["status"] == "degraded"
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    @patch.dict('os.environ', {"MASTER_API_KEY": "test-master-key"}, clear=True)
    @patch('src.service.main.check_collections_health')
    def test_health_endpoint_with_exception(self, mock_health_check, client):
        """Test health endpoint when health check fails."""
        # Clear global key manager to force reload
        from src.auth import secure_key_manager
        secure_key_manager._key_manager = None
        
        # Mock health check failure
        mock_health_check.side_effect = Exception("Qdrant connection failed")
        
        headers = {"X-API-Key": "test-master-key"}
        response = client.get("/healthz", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data
        assert "Qdrant connection failed" in data["error"]
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_health_endpoint_with_invalid_key(self, client):
        """Test health endpoint with invalid API key."""
        with patch.dict('os.environ', {"MASTER_API_KEY": "valid-key"}, clear=True):
            # Clear global key manager to force reload
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None
            
            headers = {"X-API-Key": "invalid-key"}
            response = client.get("/healthz", headers=headers)
            
            assert response.status_code == 401
            assert response.json()["detail"] == "Invalid API key"
    
    @patch('src.auth.secure_key_manager._key_manager', None)
    @patch.dict('os.environ', {"USER_API_KEY_1": "user-key"}, clear=True) 
    @patch('src.service.main.check_collections_health')
    @patch('src.service.main.logger')
    def test_health_endpoint_logs_access(self, mock_logger, mock_health_check, client):
        """Test that health endpoint logs access for audit purposes."""
        # Clear global key manager to force reload
        from src.auth import secure_key_manager
        secure_key_manager._key_manager = None
        
        # Mock healthy status
        mock_health_check.return_value = {"status": "healthy"}
        
        headers = {"X-API-Key": "user-key"}
        response = client.get("/healthz", headers=headers)
        
        assert response.status_code == 200
        
        # Verify audit logging occurred
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args
        assert "Health check accessed" in call_args[0][0]
        assert "api_key_prefix" in call_args[1]
        assert "health_status" in call_args[1]