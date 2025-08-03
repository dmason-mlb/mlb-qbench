"""Authentication implementation for MLB QBench API."""

from typing import Optional, Tuple

import structlog
from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from .secure_key_manager import verify_api_key_secure, is_master_key, get_key_info

# Load environment variables
load_dotenv()

logger = structlog.get_logger()

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str) -> bool:
    """
    Verify if the provided API key is valid.
    
    DEPRECATED: Use verify_api_key_with_info for better security tracking.
    """
    key_id = verify_api_key_secure(api_key)
    return key_id is not None


def verify_api_key_with_info(api_key: str) -> Tuple[bool, Optional[str], bool]:
    """
    Verify API key and return validation info.
    
    Args:
        api_key: The API key to verify
        
    Returns:
        Tuple of (is_valid, key_id, is_master)
    """
    if not api_key:
        return False, None, False
    
    key_id = verify_api_key_secure(api_key)
    if key_id is None:
        return False, None, False
    
    # Check if it's a master key
    is_master = is_master_key(key_id)
    
    return True, key_id, is_master


async def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Validate API key from request header with enhanced security tracking."""
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    is_valid, key_id, is_master = verify_api_key_with_info(api_key)
    
    if not is_valid:
        # Enhanced logging without exposing key details
        logger.warning(
            "Invalid API key attempted",
            key_length=len(api_key),
            key_prefix=api_key[:4] + "..." if len(api_key) > 4 else "***",
            extra={"security_event": True}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Log successful authentication with key metadata
    key_info = get_key_info(key_id) if key_id else None
    logger.info(
        "API key authenticated successfully",
        key_id=key_id,
        key_type=key_info.key_type.value if key_info else "unknown",
        is_master=is_master,
        usage_count=key_info.usage_count if key_info else 0
    )

    return api_key


async def get_api_key_with_info(api_key: Optional[str] = Security(api_key_header)) -> Tuple[str, str, bool]:
    """
    Validate API key and return key info.
    
    Returns:
        Tuple of (api_key, key_id, is_master)
    """
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    is_valid, key_id, is_master = verify_api_key_with_info(api_key)
    
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

    return api_key, key_id, is_master


# Dependency for protected endpoints
require_api_key = Security(get_api_key)
