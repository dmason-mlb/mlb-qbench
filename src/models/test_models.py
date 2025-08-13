"""Pydantic models for test data structures."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict


class TestStep(BaseModel):
    """Individual test step model."""

    index: int = Field(..., description="Step index (1-based)")
    action: str = Field(..., description="Action to perform")
    expected: list[str] = Field(default_factory=list, description="Expected results")

    @field_validator('index')
    @classmethod
    def validate_index(cls, v):
        if v < 1:
            raise ValueError("Step index must be >= 1")
        return v


class TestDoc(BaseModel):
    """Normalized test document model."""

    # Identifiers
    testId: Optional[int] = Field(None, description="Auto-incrementing unique test identifier")
    uid: str = Field(..., description="Unique identifier (jiraKey or testCaseId)")
    jiraKey: Optional[str] = Field(None, description="JIRA issue key")
    testCaseId: Optional[str] = Field(None, description="Test case ID")

    # Basic information
    title: str = Field(..., description="Test title")
    summary: Optional[str] = Field(None, description="Test summary")
    description: Optional[str] = Field(None, description="Detailed description")

    # Classification
    testType: Literal["Manual", "API", "Performance", "Integration", "Unit"] = Field(
        "Manual", description="Type of test"
    )
    priority: Literal["Critical", "High", "Medium", "Low"] = Field(
        "Medium", description="Test priority"
    )
    platforms: list[str] = Field(default_factory=list, description="Target platforms")

    # Organization
    tags: list[str] = Field(default_factory=list, description="Test tags/labels")
    folderStructure: Optional[str] = Field(None, description="Folder path in test repository")

    # Test details
    preconditions: list[str] = Field(default_factory=list, description="Test preconditions")
    steps: list[TestStep] = Field(default_factory=list, description="Test steps")
    expectedResults: Optional[str] = Field(None, description="Overall expected results")
    testData: Optional[str] = Field(None, description="Test data requirements")

    # References
    relatedIssues: list[str] = Field(default_factory=list, description="Related JIRA issues")
    testPath: Optional[str] = Field(None, description="File path in codebase")

    # Metadata
    source: Literal["functional_tests_xray.json", "api_tests_xray.json"] = Field(
        ..., description="Source file"
    )
    ingested_at: datetime = Field(default_factory=datetime.utcnow, description="Ingestion timestamp")

    @field_validator('uid')
    @classmethod
    def validate_uid(cls, v):
        if not v or not v.strip():
            raise ValueError("uid cannot be empty")
        return v.strip()

    @field_validator('tags', 'platforms', 'relatedIssues', mode='before')
    @classmethod
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)

    model_config = ConfigDict(
        # Pydantic V2: json_encoders is deprecated, use field serializers instead
    )


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    top_k: int = Field(20, ge=1, le=100, description="Number of results to return")
    filters: Optional[dict] = Field(None, description="Optional filters (will be validated for security)")
    scope: Literal["all", "docs", "steps"] = Field("all", description="Search scope")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate search query for security."""
        import re

        # Remove any potentially dangerous characters
        if re.search(r'[<>&"\']', v):
            raise ValueError("Search query contains potentially dangerous characters")

        # Check for SQL injection patterns (though we're using vector DB)
        sql_patterns = [
            r'\bUNION\b', r'\bSELECT\b', r'\bINSERT\b', r'\bDELETE\b',
            r'\bDROP\b', r'\bCREATE\b', r'\bALTER\b', r'\-\-', r'/\*'
        ]
        for pattern in sql_patterns:
            if re.search(pattern, v.upper()):
                raise ValueError("Search query contains potentially dangerous SQL patterns")

        return v.strip()


class SearchResult(BaseModel):
    """Search result model."""

    test: TestDoc = Field(..., description="Test document")
    score: float = Field(..., description="Relevance score")
    matched_steps: list[int] = Field(default_factory=list, description="Matched step indices")


class IngestRequest(BaseModel):
    """Ingestion request model."""

    functional_path: Optional[str] = Field(None, description="Path to functional tests JSON")
    api_path: Optional[str] = Field(None, description="Path to API tests JSON")

    @model_validator(mode='after')
    def at_least_one_path(self):
        if not self.functional_path and not self.api_path:
            raise ValueError("At least one path must be provided")
        return self


class IngestResponse(BaseModel):
    """Ingestion response model."""

    functional_ingested: int = Field(0, description="Number of functional tests ingested")
    api_ingested: int = Field(0, description="Number of API tests ingested")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: list[str] = Field(default_factory=list, description="Any warnings generated")


class UpdateJiraKeyRequest(BaseModel):
    """Request model for updating a test's JIRA key."""
    
    jiraKey: str = Field(..., min_length=1, max_length=50, description="New JIRA issue key")
    
    @field_validator('jiraKey')
    @classmethod
    def validate_jira_key(cls, v: str) -> str:
        """Validate JIRA key format."""
        import re
        # JIRA keys typically follow pattern: PROJECT-NUMBER
        if not re.match(r'^[A-Z][A-Z0-9]+-\d+$', v.strip().upper()):
            raise ValueError("Invalid JIRA key format. Expected format: PROJECT-123")
        return v.strip().upper()
