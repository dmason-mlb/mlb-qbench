"""Authentication implementation for MLB QBench API."""

import hmac
import os
from typing import Optional

import structlog
from dotenv import load_dotenv
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

# Load environment variables
load_dotenv()

logger = structlog.get_logger()

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Get API keys from environment
API_KEYS = os.getenv("API_KEYS", "").split(",") if os.getenv("API_KEYS") else []
MASTER_API_KEY = os.getenv("MASTER_API_KEY")



def verify_api_key(api_key: str) -> bool:
    """Verify if the provided API key is valid."""
    if not api_key:
        return False

    # Check against master key if configured
    if MASTER_API_KEY and hmac.compare_digest(api_key, MASTER_API_KEY):
        return True

    # Check against configured API keys
    for valid_key in API_KEYS:
        if valid_key and hmac.compare_digest(api_key, valid_key.strip()):
            return True
    return False


async def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Validate API key from request header."""
    if not api_key:
        logger.warning("Missing API key in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not verify_api_key(api_key):
        logger.warning("Invalid API key attempted", api_key_prefix=api_key[:8] + "...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


# Dependency for protected endpoints
require_api_key = Security(get_api_key)
