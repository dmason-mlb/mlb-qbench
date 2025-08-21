# MCP Server Improvement Opportunities

This document tracks improvement opportunities identified during the TOOLSET.md documentation generation and codebase analysis.

## Priority Improvements

### 1. Add Rate Limiting Documentation to Tool Code
**Location**: `src/mcp/server.py`  
**Issue**: Rate limits are mentioned in documentation (60/min for search, 5/min for ingestion) but not in the tool registration code itself.  
**Action**: Add rate limit information to docstrings and consider adding it to tool schemas as metadata.

```python
# Example enhancement for tool registration
types.Tool(
    name="search_tests",
    description="Search for tests using semantic search with optional filters (Rate limited: 60/min)",
    # Or add metadata field
    metadata={"rate_limit": "60/minute"},
    ...
)
```

### 2. Synchronize PostgreSQL Server Implementation
**Location**: `src/mcp/server_postgres.py`  
**Issues**:
- Missing `ingest_tests` tool (available in HTTP version but not PostgreSQL version)
- Inconsistent parameter naming: `uid` vs `jira_key` in `find_similar_tests`
- Different server name: `mlb-qbench-postgres` vs `mlb-qbench`

**Actions**:
- Add `ingest_tests` tool to PostgreSQL implementation
- Standardize parameter names across both implementations
- Consider merging implementations with a configuration flag

### 3. Add Versioning Metadata to Tools
**Location**: `src/mcp/server.py`, `src/mcp/server_postgres.py`  
**Issue**: No version tracking for individual tools makes it difficult to track API changes.  
**Action**: Add version metadata to tool definitions for better change tracking.

```python
types.Tool(
    name="search_tests",
    version="1.0.0",  # Add semantic versioning
    stability="stable",  # Add stability markers
    ...
)
```

## Additional Enhancements

### 4. Consolidate Server Implementations
**Rationale**: Having two separate MCP server files creates maintenance overhead and potential for drift.  
**Proposal**: Create a single server with configurable backend:
```python
# Unified server with backend selection
backend = os.environ.get("MCP_BACKEND", "http")  # "http" or "postgres"
if backend == "postgres":
    handler = PostgresHandler()
else:
    handler = HTTPHandler()
```

### 5. Add Tool Telemetry
**Location**: Tool execution handlers  
**Enhancement**: Track tool usage metrics for monitoring and optimization:
- Execution counts per tool
- Average response times
- Error rates by tool
- Most common filter combinations

### 6. Enhance Error Response Formatting
**Current**: Basic error text responses  
**Enhancement**: Structured error responses with:
- Error codes for programmatic handling
- Suggested fixes or alternatives
- Links to relevant documentation

### 7. Add Tool Input Validation
**Current**: Relies on JSON schema validation  
**Enhancement**: Add business logic validation:
- Validate JIRA key format before lookup
- Check file paths exist before ingestion
- Validate top_k ranges based on collection size

### 8. Implement Tool Aliases
**Enhancement**: Allow shorter or alternative tool names for common operations:
```python
aliases = {
    "search": "search_tests",
    "lookup": "get_test_by_jira",
    "similar": "find_similar_tests",
    "health": "check_health",
    "ingest": "ingest_tests"
}
```

## Documentation Improvements

### 9. Add Interactive Examples
**Location**: `docs/TOOLSET.md`  
**Enhancement**: Add runnable examples using the MCP CLI or test client

### 10. Create Tool Migration Guide
**Need**: Guide for migrating from Qdrant to PostgreSQL backend  
**Content**:
- Configuration changes required
- Performance differences
- Feature parity matrix
- Migration scripts

## Testing Improvements

### 11. Add MCP Server Integration Tests
**Location**: `tests/mcp/`  
**Coverage**:
- Tool registration validation
- Input schema compliance
- Error handling scenarios
- Rate limiting behavior
- Backend switching

### 12. Create Tool Performance Benchmarks
**Metrics to track**:
- Tool response times under load
- Memory usage during large result sets
- Embedding generation throughput
- Database query performance

## Implementation Priority

1. **High Priority** (Critical for production):
   - Synchronize PostgreSQL server implementation (#2)
   - Add rate limiting documentation (#1)

2. **Medium Priority** (Improves maintainability):
   - Add versioning metadata (#3)
   - Consolidate server implementations (#4)
   - Add MCP server integration tests (#11)

3. **Low Priority** (Nice to have):
   - Tool aliases (#8)
   - Interactive examples (#9)
   - Enhanced telemetry (#5)

## Contributor Experience & Documentation

### 13. Create CODE_OF_CONDUCT.md
**Location**: Root directory  
**Issue**: No code of conduct file exists for contributor guidelines  
**Action**: Add standard code of conduct to establish community standards and expectations for behavior.

### 14. Create SECURITY.md
**Location**: Root directory  
**Issue**: No security policy for vulnerability reporting  
**Action**: Add security policy with clear instructions for reporting vulnerabilities privately to maintainer.

### 15. Add GitHub CI/CD Workflows
**Location**: `.github/workflows/`  
**Issue**: No continuous integration setup for automated testing  
**Action**: Create CI workflow for:
- Running tests on push/PR
- Linting and formatting checks
- PostgreSQL service for integration tests
- Coverage reporting

### 16. Create CODEOWNERS File
**Location**: Root or `.github/`  
**Issue**: No automatic review assignment for PRs  
**Action**: Define code ownership for automatic reviewer assignment on different parts of codebase.

### 17. Add Pre-commit Hooks Configuration
**Location**: `.pre-commit-config.yaml`  
**Issue**: No pre-commit hooks for automatic quality checks  
**Action**: Configure pre-commit hooks for:
- Black formatting
- Ruff linting
- Mypy type checking
- Trailing whitespace removal

### 18. Create GitHub Issue and PR Templates
**Location**: `.github/ISSUE_TEMPLATE/`, `.github/pull_request_template.md`  
**Issue**: No templates for consistent issue/PR submissions  
**Action**: Add templates for:
- Bug reports
- Feature requests
- Pull request descriptions
- Security vulnerabilities (private)

### 19. Start Maintaining CHANGELOG.md
**Location**: Root directory  
**Issue**: No changelog for tracking releases and changes  
**Action**: Create changelog following Keep a Changelog format for version tracking.

### 20. Standardize Python Version Requirements
**Location**: `pyproject.toml`, various config files  
**Issue**: Mixed Python version requirements (3.9 in configs, 3.10+ in requires-python)  
**Action**: Standardize on Python 3.10+ throughout all configuration files.

### 21. Enhance Docker Development Support
**Location**: `docker-compose.yml`  
**Issue**: Docker Compose only includes PostgreSQL, not the API service  
**Action**: Add API service to docker-compose for complete containerized development environment.

### 22. Update CONTRIBUTING.md for PostgreSQL Migration
**Location**: `CONTRIBUTING.md`  
**Issue**: Many references to Qdrant instead of PostgreSQL  
**Action**: Already addressed in CONTRIBUTING.md update, but verify all documentation is synchronized.

## Implementation Priority

1. **High Priority** (Critical for production):
   - Synchronize PostgreSQL server implementation (#2)
   - Add rate limiting documentation (#1)
   - Create SECURITY.md (#14)

2. **Medium Priority** (Improves maintainability):
   - Add versioning metadata (#3)
   - Consolidate server implementations (#4)
   - Add MCP server integration tests (#11)
   - Add GitHub CI/CD workflows (#15)
   - Standardize Python version requirements (#20)

3. **Low Priority** (Nice to have):
   - Tool aliases (#8)
   - Interactive examples (#9)
   - Enhanced telemetry (#5)
   - Create CODE_OF_CONDUCT.md (#13)
   - Add pre-commit hooks (#17)
   - GitHub templates (#18)
   - Start CHANGELOG.md (#19)
   - Enhance Docker support (#21)

## Notes

- All improvements should maintain backward compatibility with existing MCP clients
- Consider creating a `v2` namespace for breaking changes
- Update CHANGELOG.md when implementing any of these improvements
- Coordinate with API versioning strategy for the FastAPI backend
- Follow-up items #13-22 were identified during CONTRIBUTING.md audit (2025-08-17)