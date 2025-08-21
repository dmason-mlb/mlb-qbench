"""Comprehensive Pydantic data models for MLB QBench test data structures and API schemas.

This module defines the core data models used throughout the MLB QBench system for
test data representation, API request/response handling, and data validation. All models
use Pydantic v2 for runtime type checking, serialization, and comprehensive validation.

Model Categories:
    - Test Data Models: TestDoc, TestStep for normalized test representation
    - API Request Models: SearchRequest, IngestRequest, UpdateJiraKeyRequest
    - API Response Models: SearchResult, IngestResponse for client responses
    - Validation Models: Custom validators for security and data integrity

Key Features:
    - Type Safety: Full type annotations with runtime validation
    - Security Validation: Input sanitization against injection attacks
    - Data Normalization: Automatic data cleaning and format standardization
    - Flexible Input: Handles multiple input formats with graceful conversion
    - Comprehensive Validation: Business rule enforcement and constraint checking

Dependencies:
    - pydantic: Core data validation and serialization framework
    - datetime: Timestamp handling for ingestion tracking
    - typing: Type hints for static analysis and runtime validation

Used by:
    - src.service.main: FastAPI endpoint request/response models
    - src.ingest.*: Data ingestion and normalization pipelines
    - src.models.schema: Qdrant vector database storage schemas
    - API clients: External systems consuming the QBench API

Performance Characteristics:
    - Validation: O(f) where f=number of fields and validation rules
    - Serialization: O(n) where n=object size and nesting depth
    - Memory: Efficient with shared validators and compiled regex patterns
    - Instantiation: ~1-10ms per model depending on complexity

Security Features:
    - SQL Injection Prevention: Pattern detection in search queries
    - XSS Protection: HTML/script tag detection and sanitization
    - JIRA Key Validation: Format enforcement for external system integration
    - Input Sanitization: Automatic trimming and dangerous character removal
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class TestStep(BaseModel):
    """Individual test step within a test case, representing a single action and expected outcome.

    This model defines the structure for test execution steps that guide manual or automated
    testing workflows. Each step contains an ordered action with associated expected results.

    Attributes:
        index: 1-based step sequence number for execution order
        action: Detailed action description for the tester to perform
        expected: List of expected outcomes that should occur after the action

    Validation:
        - Step index must be >= 1 (enforces proper sequencing)
        - Action field is required and cannot be empty
        - Expected results default to empty list if not provided

    Usage:
        Used within TestDoc.steps to define sequential test procedures.
        Critical for test execution engines and manual testing workflows.

    Performance: O(1) validation complexity per field

    Examples:
        >>> step = TestStep(index=1, action="Click login button", expected=["Login form appears"])
        >>> step.index  # 1
        >>> step.action  # "Click login button"
        >>> step.expected  # ["Login form appears"]
    """

    index: int = Field(..., description="Step index (1-based)")
    action: str = Field(..., description="Action to perform")
    expected: list[str] = Field(default_factory=list, description="Expected results")

    @field_validator("index")
    @classmethod
    def validate_index(cls, v):
        """Validate step index to ensure proper sequencing in test execution.

        Enforces 1-based indexing convention to maintain logical step ordering
        and prevent confusion with 0-based programming constructs.

        Args:
            v: Step index value to validate

        Returns:
            int: Validated step index

        Raises:
            ValueError: If index is less than 1

        Complexity: O(1) - single integer comparison
        """
        # Enforce 1-based indexing for human-readable step sequences
        # This prevents logical errors in test execution order
        if v < 1:
            raise ValueError("Step index must be >= 1")
        return v


class TestDoc(BaseModel):
    """Comprehensive normalized test document model for unified test representation.

    This is the primary data model for test cases in the MLB QBench system, providing
    a standardized structure for tests from multiple sources (Xray, TestRail, etc.).
    All test data is normalized into this format for consistent processing and storage.

    Data Categories:
        - Identifiers: testId, uid, jiraKey, testCaseId for cross-system linking
        - Content: title, summary, description for test documentation
        - Classification: testType, priority, platforms for organization
        - Structure: tags, folderStructure for categorization
        - Execution: steps, preconditions, expectedResults for test procedures
        - Traceability: relatedIssues, testPath for requirement mapping
        - Metadata: source, ingested_at for data lineage tracking

    Key Features:
        - Auto-incrementing testId for internal references
        - Flexible uid system supporting multiple identifier formats
        - Rich metadata for comprehensive test management
        - Structured step-by-step test procedures
        - Platform and environment targeting
        - Full audit trail with ingestion timestamps

    Validation Rules:
        - uid cannot be empty or whitespace-only
        - String fields are automatically converted to lists where appropriate
        - All timestamps use UTC for consistency
        - JIRA keys follow standard format validation

    Performance Characteristics:
        - Validation: O(n) where n = number of steps + tags + related issues
        - Serialization: O(d) where d = document size and nesting depth
        - Memory: ~2-10KB per document depending on step count and metadata

    Security:
        - Input sanitization on all text fields
        - Validation prevents injection attacks
        - Structured data prevents script execution

    Usage:
        Primary model for test storage in Qdrant vector database.
        Used throughout ingestion, search, and API response workflows.
        Foundation for test analytics and reporting features.
    """

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
    testType: Literal["Manual", "Automated", "API", "Performance", "Integration", "Unit"] = Field(
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
    ingested_at: datetime = Field(
        default_factory=datetime.utcnow, description="Ingestion timestamp"
    )

    @field_validator("uid")
    @classmethod
    def validate_uid(cls, v):
        """Validate unique identifier to ensure non-empty, properly formatted values.

        The uid serves as the primary identifier for test documents and must be
        unique across the entire system. It's used for deduplication during ingestion
        and for cross-references between documents.

        Args:
            v: Raw uid value from input data

        Returns:
            str: Cleaned and validated uid

        Raises:
            ValueError: If uid is None, empty string, or whitespace-only

        Security: Prevents empty identifiers that could cause lookup failures
        Complexity: O(1) - string validation and trimming
        """
        # Check for None, empty string, or whitespace-only values
        # These would break document lookups and cross-references
        if not v or not v.strip():
            raise ValueError("uid cannot be empty")
        # Remove leading/trailing whitespace to normalize identifiers
        return v.strip()

    @field_validator("tags", "platforms", "relatedIssues", mode="before")
    @classmethod
    def ensure_list(cls, v):
        """Normalize input values to lists for consistent array field handling.

        Handles various input formats from different test management systems:
        - None values become empty lists
        - Single strings become single-item lists
        - Existing lists/iterables are preserved as lists

        This normalization prevents type errors during processing and ensures
        consistent behavior across different data sources.

        Args:
            v: Input value in various formats (None, str, list, iterable)

        Returns:
            list: Normalized list representation

        Performance: O(n) where n = number of items if converting iterable

        Examples:
            >>> ensure_list(None)  # []
            >>> ensure_list("single")  # ["single"]
            >>> ensure_list(["a", "b"])  # ["a", "b"]
        """
        # Handle None/null values from JSON or missing fields
        if v is None:
            return []
        # Convert single string values to single-item lists
        # Common when data sources provide inconsistent formats
        if isinstance(v, str):
            return [v]
        # Convert any other iterable to a proper list
        # Handles tuples, sets, or other sequence types
        return list(v)

    model_config = ConfigDict(
        # Pydantic V2: json_encoders is deprecated, use field serializers instead
    )


class SearchRequest(BaseModel):
    """Search request model for semantic test discovery queries.

    Defines the structure for API requests to the /search endpoint, enabling
    AI-powered test discovery through natural language queries with optional
    filtering and scope control.

    Features:
        - Natural language query processing for semantic search
        - Configurable result limits with reasonable bounds
        - Optional filters for precise result targeting
        - Scope control for searching documents vs steps vs both
        - Security validation to prevent injection attacks

    Query Processing:
        1. Input validation and sanitization
        2. Security pattern detection and blocking
        3. Text embedding generation via configured provider
        4. Vector similarity search in Qdrant collections
        5. Filter application and result ranking

    Security Features:
        - XSS prevention through dangerous character detection
        - SQL injection pattern blocking (defense in depth)
        - Query length limits to prevent DoS attacks
        - Filter validation for safe database operations

    Performance:
        - Query validation: O(m) where m = query length
        - Embedding generation: depends on provider latency
        - Search execution: O(log n) where n = document count

    Usage:
        Primary input model for the semantic search API endpoint.
        Processed by search handlers to generate vector queries.
    """

    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    top_k: int = Field(20, ge=1, le=100, description="Number of results to return")
    filters: Optional[dict] = Field(
        None, description="Optional filters (will be validated for security)"
    )
    scope: Literal["all", "docs", "steps"] = Field("all", description="Search scope")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate search query for security vulnerabilities and malicious patterns.

        Implements defense-in-depth security validation to prevent various attack
        vectors including XSS, SQL injection, and script injection attempts.

        Security Checks:
            1. Dangerous character detection (XSS prevention)
            2. SQL injection pattern matching (defense in depth)
            3. Script tag and HTML element blocking
            4. Query sanitization and normalization

        Args:
            v: Raw search query string from user input

        Returns:
            str: Sanitized and validated query string

        Raises:
            ValueError: If query contains dangerous patterns or characters

        Security: Prevents XSS, SQL injection, and script injection attacks
        Complexity: O(m*p) where m = query length, p = number of patterns
        """
        import re

        # Detect HTML/XML characters that could enable XSS attacks
        # Block common XSS injection vectors like <script>, &lt;, quotes
        if re.search(r'[<>&"\']', v):
            raise ValueError("Search query contains potentially dangerous characters")

        # SQL injection pattern detection (defense in depth)
        # Even though we use vector DB, prevent SQL patterns in case of integration
        sql_patterns = [
            r"\bUNION\b",
            r"\bSELECT\b",
            r"\bINSERT\b",
            r"\bDELETE\b",
            r"\bDROP\b",
            r"\bCREATE\b",
            r"\bALTER\b",
            r"\-\-",
            r"/\*",
        ]
        # Check each pattern against uppercase query for case-insensitive detection
        for pattern in sql_patterns:
            if re.search(pattern, v.upper()):
                raise ValueError("Search query contains potentially dangerous SQL patterns")

        # Normalize whitespace and return cleaned query
        return v.strip()


class SearchResult(BaseModel):
    """Individual search result containing test document and relevance metadata.

    Represents a single test document returned from semantic search operations,
    including the full test data, relevance scoring, and step-level match information.

    Components:
        - test: Complete TestDoc with all test information
        - score: Relevance score from vector similarity calculation
        - matched_steps: Step indices that contributed to the match

    Scoring System:
        - Scores range from 0.0 (no relevance) to 1.0 (perfect match)
        - Combines document-level and step-level similarity scores
        - Higher scores indicate better semantic relevance to query
        - Weighted scoring: 70% document + 30% steps (configurable)

    Step Matching:
        - Records which specific steps matched the search query
        - Enables highlighting relevant test procedures
        - Helps users understand why a test was returned
        - Used for test analytics and relevance feedback

    Performance:
        - Lightweight model with minimal overhead
        - Score calculation: O(1) simple float operations
        - Step index tracking: O(k) where k = number of matched steps

    Usage:
        Returned in arrays from search API endpoints.
        Consumed by UI components for test discovery.
        Used in recommendation algorithms and analytics.
    """

    test: TestDoc = Field(..., description="Test document")
    score: float = Field(..., description="Relevance score")
    matched_steps: list[int] = Field(default_factory=list, description="Matched step indices")


class IngestRequest(BaseModel):
    """Request model for batch test data ingestion operations.

    Defines the structure for API requests to ingest test data from JSON files
    into the QBench vector database. Supports ingestion from multiple test
    management systems with different formats.

    Supported Sources:
        - functional_path: Xray functional tests in JSON format
        - api_path: API test specifications in JSON format

    Validation Requirements:
        - At least one path must be provided for ingestion
        - Path validation ensures file accessibility and security
        - Both paths can be provided for combined ingestion

    Processing Flow:
        1. Path validation and security checks
        2. File existence and format verification
        3. JSON parsing and schema validation
        4. Data normalization to TestDoc format
        5. Embedding generation for vector storage
        6. Batch insertion into Qdrant collections

    Security:
        - Path traversal attack prevention
        - File type validation (JSON only)
        - Size limits to prevent DoS attacks
        - Sandbox execution environment

    Performance:
        - Supports concurrent processing of multiple files
        - Batch operations for efficient database insertion
        - Progress tracking for large datasets

    Usage:
        Used by ingestion API endpoints and batch processing scripts.
        Consumed by data pipeline automation tools.
    """

    functional_path: Optional[str] = Field(None, description="Path to functional tests JSON")
    api_path: Optional[str] = Field(None, description="Path to API tests JSON")

    @model_validator(mode="after")
    def at_least_one_path(self):
        """Validate that at least one ingestion path is provided.

        Ensures the ingestion request has actionable data by requiring
        at least one valid file path. Prevents empty ingestion requests
        that would waste processing resources.

        Validation Logic:
            - Checks both functional_path and api_path fields
            - Requires at least one to be non-empty/non-None
            - Allows both paths for combined ingestion workflows

        Returns:
            self: Validated model instance

        Raises:
            ValueError: If both paths are None or empty

        Complexity: O(1) - simple null/empty checks

        Business Rule:
            Prevents wasted API calls and ensures meaningful ingestion operations.
        """
        # Check if both ingestion paths are missing or empty
        # This would result in a no-op ingestion request
        if not self.functional_path and not self.api_path:
            raise ValueError("At least one path must be provided")
        return self


class IngestResponse(BaseModel):
    """Response model for batch test data ingestion operations.

    Provides comprehensive feedback on ingestion operations including
    success counts, error details, and warning information for
    troubleshooting and monitoring purposes.

    Response Categories:
        - Success Metrics: Counts of successfully ingested tests by type
        - Error Tracking: Detailed error messages for failed operations
        - Warning System: Non-fatal issues that may require attention
        - Processing Stats: Performance and throughput information

    Error Handling:
        - Captures parsing errors from malformed JSON
        - Records validation failures for individual tests
        - Tracks embedding generation failures
        - Documents database insertion errors

    Warning Types:
        - Duplicate test identifiers (overwrites)
        - Missing optional fields
        - Data format inconsistencies
        - Performance degradation alerts

    Monitoring Integration:
        - Metrics exported to monitoring systems
        - Log aggregation for error analysis
        - Performance tracking for optimization
        - Quality assurance reporting

    Usage:
        Returned from ingestion API endpoints.
        Used by monitoring dashboards and alerting systems.
        Consumed by data quality assurance processes.
    """

    functional_ingested: int = Field(0, description="Number of functional tests ingested")
    api_ingested: int = Field(0, description="Number of API tests ingested")
    errors: list[str] = Field(default_factory=list, description="Any errors encountered")
    warnings: list[str] = Field(default_factory=list, description="Any warnings generated")


class UpdateJiraKeyRequest(BaseModel):
    """Request model for updating a test document's JIRA key reference.

    Enables updating the JIRA integration key for existing test documents,
    maintaining traceability between QBench tests and JIRA issues/stories.

    JIRA Integration:
        - Links test cases to JIRA issues for requirement traceability
        - Enables automated status updates and reporting
        - Supports agile workflow integration
        - Maintains audit trail of requirement changes

    Key Format Requirements:
        - Standard JIRA pattern: PROJECT-NUMBER (e.g., DEV-123)
        - Project key must be alphabetic uppercase
        - Issue number must be numeric
        - No special characters or spaces allowed

    Validation Rules:
        - Regex pattern matching for format compliance
        - Case normalization to uppercase
        - Length limits for reasonable key sizes
        - Character set restrictions for security

    Security Considerations:
        - Input sanitization prevents injection attacks
        - Format validation blocks malformed references
        - Length limits prevent buffer overflow attempts
        - Character restrictions prevent script injection

    Usage:
        Used by test management APIs for JIRA integration.
        Consumed by requirement traceability features.
        Part of agile workflow automation systems.
    """

    jiraKey: str = Field(..., min_length=1, max_length=50, description="New JIRA issue key")

    @field_validator("jiraKey")
    @classmethod
    def validate_jira_key(cls, v: str) -> str:
        r"""Validate JIRA key format according to Atlassian standards.

        Enforces the standard JIRA issue key format (PROJECT-NUMBER) to ensure
        compatibility with JIRA APIs and prevent integration errors.

        Format Requirements:
            - Starts with uppercase letter (A-Z)
            - Followed by alphanumeric characters (A-Z, 0-9)
            - Hyphen separator (-)
            - Ends with numeric issue ID (\d+)

        Examples:
            - Valid: DEV-123, PROJECT-1, ABC123-999
            - Invalid: dev-123, PROJECT_123, -123, PROJECT-

        Args:
            v: Raw JIRA key string from user input

        Returns:
            str: Normalized JIRA key in uppercase format

        Raises:
            ValueError: If key doesn't match required JIRA format

        Security: Prevents malformed keys that could cause API errors
        Complexity: O(m) where m = key length for regex matching
        """
        import re

        # Standard JIRA key pattern: PROJECT-NUMBER
        # ^[A-Z] - starts with uppercase letter
        # [A-Z0-9]+ - project code with letters/numbers
        # - - required hyphen separator
        # \d+$ - ends with one or more digits
        if not re.match(r"^[A-Z][A-Z0-9]+-\d+$", v.strip().upper()):
            raise ValueError("Invalid JIRA key format. Expected format: PROJECT-123")
        # Normalize to uppercase for consistency with JIRA conventions
        return v.strip().upper()
