"""Authentication models for MLB QBench API key management.

This module defines Pydantic models for API key authentication and authorization.
These models provide type-safe validation for API key data structures used
throughout the authentication system.

Authentication Models:
    - APIKeyAuth: Complete API key configuration with metadata
    - Scope-based authorization support for fine-grained access control
    - Activity status tracking for key lifecycle management

Dependencies:
    - pydantic: For data validation and serialization
    - typing: For type annotations and optional fields

Used by:
    - src.auth.secure_key_manager: For API key storage and validation
    - src.auth.auth: For authentication workflow validation
    - src.service.main: For API key configuration endpoints
    - Administrative tools: For API key management operations

Data Flow:
    Configuration → Validation → Storage → Authentication → Authorization

Complexity:
    - Model validation: O(1) per field validation
    - Serialization: O(n) where n is number of scopes
    - Field access: O(1) direct attribute access
"""

from typing import Optional

from pydantic import BaseModel


class APIKeyAuth(BaseModel):
    """API key authentication model with comprehensive metadata and validation.
    
    This model represents a complete API key configuration including the key itself,
    descriptive metadata, activation status, and scope-based permissions. It provides
    type-safe validation for all API key operations.
    
    Security Features:
        - Immutable key storage once created
        - Boolean activation status for quick enable/disable
        - Scope-based authorization for granular permissions
        - Optional description for audit trail and management
        
    Validation Rules:
        - api_key: Required string, validated at Pydantic level
        - description: Optional string for human-readable identification
        - is_active: Boolean flag, defaults to True for immediate activation
        - scopes: List of permission strings, defaults to empty (no special permissions)
        
    Performance:
        - Validation: O(1) for most fields, O(n) for scopes where n=scope count
        - Serialization: O(n) where n is total field count + scope count
        - Memory: O(k + s) where k=key length, s=total scope string length
        
    Usage Example:
        key_config = APIKeyAuth(
            api_key="secret-key-value",
            description="Production API access for service X",
            is_active=True,
            scopes=["read:tests", "write:results"]
        )
    """
    
    # Primary API key value (required for all operations)
    # This should be a cryptographically secure random string
    api_key: str
    
    # Human-readable description for management and audit purposes
    # Used for identifying keys in administrative interfaces
    description: Optional[str] = None
    
    # Activation status for quick enable/disable without deletion
    # Allows temporary deactivation while preserving configuration
    is_active: bool = True
    
    # Scope-based permissions for fine-grained access control
    # Empty list means basic access only, specific scopes grant additional permissions
    # Common scopes: "read:tests", "write:tests", "admin:all", "ingest:data"
    scopes: list[str] = []
