"""Authentication models."""

from typing import Optional

from pydantic import BaseModel


class APIKeyAuth(BaseModel):
    """API Key authentication model."""
    api_key: str
    description: Optional[str] = None
    is_active: bool = True
    scopes: list[str] = []
