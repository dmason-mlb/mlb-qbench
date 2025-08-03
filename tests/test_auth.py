"""Test authentication functionality."""

import os
import pytest
from unittest.mock import patch
from fastapi import HTTPException

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.auth import verify_api_key, get_api_key


class TestAuthentication:
    """Test authentication functions."""

    def test_verify_api_key_with_master_key(self):
        """Test API key verification with master key."""
        with patch.dict(os.environ, {"MASTER_API_KEY": "test-master-key"}):
            # Reload the module to pick up env changes
            from src.auth import auth
            auth.MASTER_API_KEY = "test-master-key"
            
            assert auth.verify_api_key("test-master-key") is True
            assert auth.verify_api_key("wrong-key") is False
            assert auth.verify_api_key("") is False

    def test_verify_api_key_with_api_keys_list(self):
        """Test API key verification with API keys list."""
        with patch.dict(os.environ, {"API_KEYS": "key1,key2,key3"}):
            # Reload the module to pick up env changes
            from src.auth import auth
            auth.API_KEYS = ["key1", "key2", "key3"]
            
            assert auth.verify_api_key("key1") is True
            assert auth.verify_api_key("key2") is True
            assert auth.verify_api_key("key3") is True
            assert auth.verify_api_key("wrong-key") is False

    def test_verify_api_key_no_keys_configured(self):
        """Test API key verification when no keys are configured."""
        with patch.dict(os.environ, {"MASTER_API_KEY": "", "API_KEYS": ""}):
            # Reload the module to pick up env changes
            from src.auth import auth
            auth.MASTER_API_KEY = ""
            auth.API_KEYS = []
            
            assert auth.verify_api_key("any-key") is False

    @pytest.mark.asyncio
    async def test_get_api_key_missing_header(self):
        """Test get_api_key when header is missing."""
        with pytest.raises(HTTPException) as exc_info:
            await get_api_key(None)
        
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Missing API key"

    @pytest.mark.asyncio
    async def test_get_api_key_invalid_key(self):
        """Test get_api_key with invalid key."""
        with patch.dict(os.environ, {"MASTER_API_KEY": "valid-key"}):
            # Reload the module to pick up env changes
            from src.auth import auth
            auth.MASTER_API_KEY = "valid-key"
            
            with pytest.raises(HTTPException) as exc_info:
                await auth.get_api_key("invalid-key")
            
            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid API key"

    @pytest.mark.asyncio
    async def test_get_api_key_valid_key(self):
        """Test get_api_key with valid key."""
        with patch.dict(os.environ, {"MASTER_API_KEY": "valid-key"}):
            # Reload the module to pick up env changes
            from src.auth import auth
            auth.MASTER_API_KEY = "valid-key"
            
            result = await auth.get_api_key("valid-key")
            assert result == "valid-key"