"""Test authentication functionality."""

import os
import sys
from unittest.mock import patch

import pytest
from fastapi import HTTPException

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth.auth import get_api_key, verify_api_key, verify_api_key_with_info


class TestAuthentication:
    """Test authentication functions."""

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_verify_api_key_with_master_key(self):
        """Test API key verification with master key."""
        with patch.dict(os.environ, {"MASTER_API_KEY": "test-master-key"}, clear=True):
            # Clear global key manager to force reload
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            assert verify_api_key("test-master-key") is True
            assert verify_api_key("wrong-key") is False
            assert verify_api_key("") is False

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_verify_api_key_with_user_keys(self):
        """Test API key verification with individual user keys."""
        with patch.dict(os.environ, {
            "USER_API_KEY_1": "user-key-1",
            "USER_API_KEY_2": "user-key-2",
            "USER_API_KEY_3": "user-key-3"
        }, clear=True):
            # Clear global key manager to force reload
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            assert verify_api_key("user-key-1") is True
            assert verify_api_key("user-key-2") is True
            assert verify_api_key("user-key-3") is True
            assert verify_api_key("wrong-key") is False

    @patch('src.auth.secure_key_manager._key_manager', None)
    def test_verify_api_key_no_keys_configured(self):
        """Test API key verification when no keys are configured."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear global key manager to force reload
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            assert verify_api_key("any-key") is False

    @pytest.mark.asyncio
    async def test_get_api_key_missing_header(self):
        """Test get_api_key when header is missing."""
        with pytest.raises(HTTPException) as exc_info:
            await get_api_key(None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Missing API key"

    @pytest.mark.asyncio
    @patch('src.auth.secure_key_manager._key_manager', None)
    async def test_get_api_key_invalid_key(self):
        """Test get_api_key with invalid key."""
        with patch.dict(os.environ, {"MASTER_API_KEY": "valid-key"}, clear=True):
            # Clear global key manager to force reload
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            with pytest.raises(HTTPException) as exc_info:
                await get_api_key("invalid-key")

            assert exc_info.value.status_code == 401
            assert exc_info.value.detail == "Invalid API key"

    @pytest.mark.asyncio
    @patch('src.auth.secure_key_manager._key_manager', None)
    async def test_get_api_key_valid_key(self):
        """Test get_api_key with valid key."""
        with patch.dict(os.environ, {"MASTER_API_KEY": "valid-key"}, clear=True):
            # Clear global key manager to force reload
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            result = await get_api_key("valid-key")
            assert result == "valid-key"

    @pytest.mark.asyncio
    @patch('src.auth.secure_key_manager._key_manager', None)
    async def test_verify_api_key_with_info(self):
        """Test verify_api_key_with_info function."""
        with patch.dict(os.environ, {
            "MASTER_API_KEY": "master-key",
            "USER_API_KEY_1": "user-key-1"
        }, clear=True):
            # Clear global key manager to force reload
            from src.auth import secure_key_manager
            secure_key_manager._key_manager = None

            # Test master key
            is_valid, key_id, is_master = verify_api_key_with_info("master-key")
            assert is_valid is True
            assert key_id == "master"
            assert is_master is True

            # Test user key
            is_valid, key_id, is_master = verify_api_key_with_info("user-key-1")
            assert is_valid is True
            assert key_id == "user_1"
            assert is_master is False

            # Test invalid key
            is_valid, key_id, is_master = verify_api_key_with_info("invalid-key")
            assert is_valid is False
            assert key_id is None
            assert is_master is False
