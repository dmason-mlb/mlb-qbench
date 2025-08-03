"""Pydantic models for test data structures."""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator, field_validator


class TestStep(BaseModel):
    """Individual test step model."""
    
    index: int = Field(..., description="Step index (1-based)")
    action: str = Field(..., description="Action to perform")
    expected: List[str] = Field(default_factory=list, description="Expected results")
    
    @validator('index')
    def validate_index(cls, v):
        if v < 1:
            raise ValueError("Step index must be >= 1")
        return v


class TestDoc(BaseModel):
    """Normalized test document model."""
    
    # Identifiers
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
    platforms: List[str] = Field(default_factory=list, description="Target platforms")
    
    # Organization
    tags: List[str] = Field(default_factory=list, description="Test tags/labels")
    folderStructure: Optional[str] = Field(None, description="Folder path in test repository")
    
    # Test details
    preconditions: List[str] = Field(default_factory=list, description="Test preconditions")
    steps: List[TestStep] = Field(default_factory=list, description="Test steps")
    expectedResults: Optional[str] = Field(None, description="Overall expected results")
    testData: Optional[str] = Field(None, description="Test data requirements")
    
    # References
    relatedIssues: List[str] = Field(default_factory=list, description="Related JIRA issues")
    testPath: Optional[str] = Field(None, description="File path in codebase")
    
    # Metadata
    source: Literal["functional_tests_xray.json", "api_tests_xray.json"] = Field(
        ..., description="Source file"
    )
    ingested_at: datetime = Field(default_factory=datetime.utcnow, description="Ingestion timestamp")
    
    @validator('uid')
    def validate_uid(cls, v):
        if not v or not v.strip():
            raise ValueError("uid cannot be empty")
        return v.strip()
    
    @validator('tags', 'platforms', 'relatedIssues', pre=True)
    def ensure_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [v]
        return list(v)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


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
    matched_steps: List[int] = Field(default_factory=list, description="Matched step indices")
    
    
class IngestRequest(BaseModel):
    """Ingestion request model."""
    
    functional_path: Optional[str] = Field(None, description="Path to functional tests JSON")
    api_path: Optional[str] = Field(None, description="Path to API tests JSON")
    
    @validator('functional_path', 'api_path')
    def at_least_one_path(cls, v, values):
        if not v and not any(values.values()):
            raise ValueError("At least one path must be provided")
        return v


class IngestResponse(BaseModel):
    """Ingestion response model."""
    
    functional_ingested: int = Field(0, description="Number of functional tests ingested")
    api_ingested: int = Field(0, description="Number of API tests ingested")
    errors: List[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: List[str] = Field(default_factory=list, description="Any warnings generated")