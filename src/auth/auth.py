"""Authentication implementation for MLB QBench API.

This module provides comprehensive API key authentication for the MLB QBench service,
including secure key validation, authorization checking, and security event logging.

Authentication Features:
    - API key validation via X-API-Key header
    - Master key privileges for admin operations
    - Security event logging for monitoring
    - Rate limiting integration
    - Detailed key metadata tracking

Security Model:
    - API keys are validated using secure cryptographic functions
    - Master keys provide elevated privileges for admin operations
    - All authentication attempts are logged for security monitoring
    - Invalid keys trigger security events without exposing key details
    - Key usage statistics are tracked for monitoring

Dependencies:
    - fastapi: For HTTP authentication and security dependencies
    - structlog: For comprehensive security logging
    - secure_key_manager: For cryptographic key validation

Used by:
    - src.service.main: For protecting API endpoints
    - All protected endpoints: Via require_api_key dependency
    - Rate limiting: For key-based rate limiting

Complexity:
    - Key validation: O(1) hash lookup with cryptographic verification
    - Authentication flow: O(1) per request
    - Logging: O(1) structured logging operations
"""

from typing import Optional

import structlog
from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .secure_key_manager import get_key_info, is_master_key, verify_api_key_secure

# Load environment variables for configuration
load_dotenv()

logger = structlog.get_logger()

# API Key header scheme for FastAPI Security
# auto_error=False allows manual error handling with custom messages
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str) -> bool:
    """Verify if the provided API key is valid (DEPRECATED).
    
    DEPRECATED: Use verify_api_key_with_info() for better security tracking
    and detailed validation information. This function is maintained for
    backward compatibility but lacks the enhanced security features.

    Args:
        api_key: The API key string to verify

    Returns:
        bool: True if the key is valid, False otherwise
        
    Complexity: O(1) - Single cryptographic verification operation
    
    Security Note:
        This function does not provide key metadata or master key detection.
        Use verify_api_key_with_info() for production code.
    """
    # Delegate to secure key manager for cryptographic verification
    key_id = verify_api_key_secure(api_key)
    return key_id is not None  # Valid if key_id was returned


def verify_api_key_with_info(api_key: str) -> tuple[bool, Optional[str], bool]:
    """Verify API key and return comprehensive validation information.
    
    Performs secure API key validation and returns detailed information
    about the key, including validity, key identifier, and master key status.
    This is the preferred method for API key validation.

    Args:
        api_key: The API key string to verify

    Returns:
        Tuple containing:
        - is_valid (bool): True if the key is valid
        - key_id (Optional[str]): Unique identifier for the key, None if invalid
        - is_master (bool): True if this is a master key with elevated privileges
        
    Complexity: O(1) - Hash lookup and cryptographic verification
    
    Security Features:
        - Cryptographic key validation via secure_key_manager
        - Master key privilege detection
        - Safe handling of None/empty keys
        - No key material exposed in logs or returns
    """
    # Handle empty or None keys safely
    if not api_key:
        return False, None, False

    # Perform cryptographic verification via secure key manager
    key_id = verify_api_key_secure(api_key)
    if key_id is None:
        return False, None, False  # Invalid key

    # Check master key privileges for validated key
    is_master = is_master_key(key_id)

    return True, key_id, is_master  # Valid key with metadata


async def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Validate API key from request header with enhanced security tracking.
    
    FastAPI dependency function that validates the X-API-Key header and
    provides comprehensive security logging. This is the primary authentication
    mechanism for API endpoints.
    
    Args:
        api_key: Optional API key from X-API-Key header (injected by FastAPI)
    
    Returns:
        str: The validated API key for use in the endpoint
        
    Raises:
        HTTPException: 401 Unauthorized if:
            - API key is missing from request headers
            - API key is invalid or expired
            - API key format is incorrect
            
    Complexity: O(1) - Single validation and logging operation
    
    Security Features:
        - Secure key validation with cryptographic verification
        - Comprehensive security event logging
        - Key prefix logging (first 4 chars) for debugging without exposure
        - Authentication success tracking with key metadata
        - Master key detection and logging
        - Usage count tracking for monitoring
    """
    # Check for missing API key in request headers
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},  # Standard auth challenge
        )

    # Perform comprehensive key validation
    is_valid, key_id, is_master = verify_api_key_with_info(api_key)

    if not is_valid:
        # Enhanced security logging without exposing sensitive key material
        logger.warning(
            "Invalid API key attempted",
            key_length=len(api_key),  # Length for pattern analysis
            key_prefix=api_key[:4] + "..." if len(api_key) > 4 else "***",  # Safe prefix
            extra={"security_event": True}  # Mark for security monitoring
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Log successful authentication with comprehensive key metadata
    key_info = get_key_info(key_id) if key_id else None
    logger.info(
        "API key authenticated successfully",
        key_id=key_id,  # Internal key identifier (safe to log)
        key_type=key_info.key_type.value if key_info else "unknown",
        is_master=is_master,  # Privilege level
        usage_count=key_info.usage_count if key_info else 0  # Usage tracking
    )

    return api_key  # Return validated key for endpoint use


async def get_api_key_with_info(api_key: Optional[str] = Security(api_key_header)) -> tuple[str, str, bool]:
    """Validate API key and return comprehensive key information.
    
    Extended version of get_api_key that returns both the validated key and
    its metadata. Useful for endpoints that need to make authorization decisions
    based on key type or privileges.

    Args:
        api_key: Optional API key from X-API-Key header (injected by FastAPI)

    Returns:
        Tuple containing:
        - api_key (str): The validated API key
        - key_id (str): Internal key identifier for tracking
        - is_master (bool): True if this is a master key with elevated privileges
        
    Raises:
        HTTPException: 401 Unauthorized if authentication fails
        
    Complexity: O(1) - Same as get_api_key with additional metadata extraction
    
    Usage:
        Used by endpoints that need to check key privileges or track usage by key ID.
    """
    # Check for missing API key (same validation as get_api_key)
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Validate key and extract metadata
    is_valid, key_id, is_master = verify_api_key_with_info(api_key)

    # Check validity and ensure key_id is present (defensive programming)
    if not is_valid or not key_id:
        logger.warning(
            "Invalid API key attempted",
            key_prefix=api_key[:4] + "..." if len(api_key) > 4 else "***",
            extra={"security_event": True}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Return validated key with metadata for authorization decisions
    return api_key, key_id, is_master


# FastAPI Security dependency for protecting endpoints
# This creates a dependency that can be injected into any endpoint to require authentication
require_api_key = Security(get_api_key)
