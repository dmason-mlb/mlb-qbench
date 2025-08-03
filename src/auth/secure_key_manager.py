"""Secure API key management with hashed storage."""

import hashlib
import hmac
import os
import secrets
from typing import Dict, List, Optional, Set
from enum import Enum

import structlog
from pydantic import BaseModel, Field

logger = structlog.get_logger()


class KeyType(str, Enum):
    """Types of API keys."""
    MASTER = "master"
    USER = "user"
    SERVICE = "service"


class ApiKeyMetadata(BaseModel):
    """Metadata for an API key."""
    key_id: str = Field(..., description="Unique identifier for the key")
    key_type: KeyType = Field(..., description="Type of API key")
    description: str = Field("", description="Human-readable description")
    created_at: str = Field(..., description="ISO timestamp when key was created")
    last_used: Optional[str] = Field(None, description="ISO timestamp of last use")
    usage_count: int = Field(0, description="Number of times key has been used")
    is_active: bool = Field(True, description="Whether key is currently active")


class SecureKeyManager:
    """
    Secure API key manager that stores hashed keys and prevents exposure.
    
    Key Security Features:
    - Keys are hashed using PBKDF2 with unique salts
    - No plaintext keys stored in memory after initialization
    - Individual environment variables prevent comma-separated exposure
    - Timing-safe comparison prevents timing attacks
    - Key metadata tracking for audit purposes
    """
    
    def __init__(self):
        self._key_hashes: Dict[str, bytes] = {}
        self._key_salts: Dict[str, bytes] = {}  
        self._key_metadata: Dict[str, ApiKeyMetadata] = {}
        self._load_keys_from_environment()
    
    def _load_keys_from_environment(self) -> None:
        """Load and hash API keys from environment variables."""
        # Load master key
        master_key = os.getenv("MASTER_API_KEY")
        if master_key:
            self._add_key_hash("master", master_key, KeyType.MASTER, "Master API key")
        
        # Load numbered user keys (USER_API_KEY_1, USER_API_KEY_2, etc.)
        user_key_index = 1
        while True:
            user_key = os.getenv(f"USER_API_KEY_{user_key_index}")
            if not user_key:
                break
            
            key_id = f"user_{user_key_index}"
            description = os.getenv(f"USER_API_KEY_{user_key_index}_DESC", f"User API key {user_key_index}")
            self._add_key_hash(key_id, user_key, KeyType.USER, description)
            user_key_index += 1
        
        # Load service keys (SERVICE_API_KEY_<NAME>)
        service_key_prefixes = [var for var in os.environ.keys() if var.startswith("SERVICE_API_KEY_")]
        for env_var in service_key_prefixes:
            service_name = env_var.replace("SERVICE_API_KEY_", "").lower()
            service_key = os.getenv(env_var)
            if service_key:
                key_id = f"service_{service_name}"
                description = f"Service API key for {service_name}"
                self._add_key_hash(key_id, service_key, KeyType.SERVICE, description)
        
        logger.info(
            "Loaded API keys from environment",
            total_keys=len(self._key_hashes),
            master_key_present=bool(master_key),
            user_keys=user_key_index - 1,
            service_keys=len(service_key_prefixes)
        )
    
    def _add_key_hash(self, key_id: str, plaintext_key: str, key_type: KeyType, description: str) -> None:
        """Add a key hash to the manager."""
        # Generate unique salt for this key
        salt = secrets.token_bytes(32)
        
        # Hash the key using PBKDF2
        key_hash = hashlib.pbkdf2_hmac('sha256', plaintext_key.encode(), salt, 100000)
        
        # Store hash and salt
        self._key_hashes[key_id] = key_hash
        self._key_salts[key_id] = salt
        
        # Store metadata
        from datetime import datetime
        self._key_metadata[key_id] = ApiKeyMetadata(
            key_id=key_id,
            key_type=key_type,
            description=description,
            created_at=datetime.utcnow().isoformat()
        )
        
        # Clear plaintext key from memory as much as possible
        del plaintext_key
    
    def verify_key(self, provided_key: str) -> Optional[str]:
        """
        Verify a provided API key against stored hashes.
        
        Args:
            provided_key: The plaintext key to verify
            
        Returns:
            Key ID if valid, None if invalid
        """
        if not provided_key:
            return None
        
        # Check against all stored key hashes
        for key_id, stored_hash in self._key_hashes.items():
            salt = self._key_salts[key_id]
            
            # Hash the provided key with the same salt
            provided_hash = hashlib.pbkdf2_hmac('sha256', provided_key.encode(), salt, 100000)
            
            # Use timing-safe comparison
            if hmac.compare_digest(provided_hash, stored_hash):
                # Update usage statistics
                if key_id in self._key_metadata:
                    metadata = self._key_metadata[key_id]
                    if metadata.is_active:
                        from datetime import datetime
                        metadata.last_used = datetime.utcnow().isoformat()
                        metadata.usage_count += 1
                        
                        logger.info(
                            "API key verification successful",
                            key_id=key_id,
                            key_type=metadata.key_type.value,
                            usage_count=metadata.usage_count
                        )
                        return key_id
                    else:
                        logger.warning(
                            "Inactive API key attempted",
                            key_id=key_id,
                            key_type=metadata.key_type.value
                        )
                        return None
        
        # Log failed verification attempt
        logger.warning(
            "API key verification failed",
            provided_key_prefix=provided_key[:8] + "..." if len(provided_key) > 8 else "***"
        )
        return None
    
    def get_key_metadata(self, key_id: str) -> Optional[ApiKeyMetadata]:
        """Get metadata for a specific key."""
        return self._key_metadata.get(key_id)
    
    def list_keys(self) -> List[ApiKeyMetadata]:
        """List all key metadata (no sensitive data)."""
        return list(self._key_metadata.values())
    
    def deactivate_key(self, key_id: str) -> bool:
        """Deactivate a specific key."""
        if key_id in self._key_metadata:
            self._key_metadata[key_id].is_active = False
            logger.info("API key deactivated", key_id=key_id)
            return True
        return False
    
    def activate_key(self, key_id: str) -> bool:
        """Activate a specific key."""
        if key_id in self._key_metadata:
            self._key_metadata[key_id].is_active = True
            logger.info("API key activated", key_id=key_id)
            return True
        return False
    
    def get_key_count(self) -> Dict[str, int]:
        """Get count of keys by type."""
        counts = {key_type.value: 0 for key_type in KeyType}
        for metadata in self._key_metadata.values():
            if metadata.is_active:
                counts[metadata.key_type.value] += 1
        return counts
    
    def is_master_key(self, key_id: str) -> bool:
        """Check if a key ID represents a master key."""
        metadata = self._key_metadata.get(key_id)
        return metadata is not None and metadata.key_type == KeyType.MASTER


# Global instance
_key_manager: Optional[SecureKeyManager] = None


def get_key_manager() -> SecureKeyManager:
    """Get the global key manager instance."""
    global _key_manager
    if _key_manager is None:
        _key_manager = SecureKeyManager()
    return _key_manager


def verify_api_key_secure(api_key: str) -> Optional[str]:
    """
    Secure API key verification using the key manager.
    
    Args:
        api_key: The plaintext key to verify
        
    Returns:
        Key ID if valid, None if invalid
    """
    manager = get_key_manager()
    return manager.verify_key(api_key)


def get_key_info(key_id: str) -> Optional[ApiKeyMetadata]:
    """Get information about a specific key."""
    manager = get_key_manager()
    return manager.get_key_metadata(key_id)


def list_api_keys() -> List[ApiKeyMetadata]:
    """List all API keys (metadata only, no sensitive data)."""
    manager = get_key_manager()
    return manager.list_keys()


def is_master_key(key_id: str) -> bool:
    """Check if a key ID represents a master key."""
    manager = get_key_manager()
    return manager.is_master_key(key_id)