# MLB QBench Test Ingestion Guide

This guide provides comprehensive instructions for ingesting test data into the MLB QBench system.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Data Formats](#data-formats)
4. [Ingestion Methods](#ingestion-methods)
5. [Field Harmonization](#field-harmonization)
6. [Step-by-Step Ingestion](#step-by-step-ingestion)
7. [Validation and Monitoring](#validation-and-monitoring)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)

## Overview

MLB QBench supports ingesting test data from two primary formats:
- **Functional Tests**: Traditional test cases with steps and expected results
- **API Tests**: HTTP-based tests with request/response validation

Both formats are normalized into a unified schema and stored in two Qdrant collections:
- `test_docs`: Document-level vectors for test metadata
- `test_steps`: Step-level vectors for granular search

## Prerequisites

Before ingesting data, ensure:

1. **Services are running**:
   ```bash
   # Start Qdrant
   make qdrant-up
   
   # Verify Qdrant is healthy
   curl http://localhost:6533/health
   ```

2. **Collections exist**:
   ```bash
   # Create collections if they don't exist
   python -m src.models.schema
   ```

3. **API key is configured**:
   ```bash
   # Check environment
   make check-env
   ```

## Data Formats

### Functional Test Format

```json
{
  "rows": [
    {
      "issueId": 12345,
      "issueKey": "FRAMED-1390",
      "summary": "English Language - Team Page API",
      "labels": ["team_page", "api", "localization"],
      "priority": "High",
      "folder": "/Web/Team/Localization",
      "testScript": {
        "steps": [
          {
            "index": 1,
            "action": "Send GET request to /api/team/{teamId}",
            "data": "teamId: 119",
            "result": "200 OK response"
          }
        ]
      }
    }
  ]
}
```

### API Test Format

```json
[
  {
    "jiraKey": "API-001",
    "testCaseId": "tc_api_001",
    "title": "Verify Team Roster API",
    "tags": ["api", "roster", "team"],
    "priority": "Medium",
    "folderStructure": ["API", "Team", "Roster"],
    "steps": [
      {
        "index": 1,
        "action": "GET /api/team/119/roster",
        "expected": ["Status: 200", "Contains player data"]
      }
    ]
  }
]
```

### Handling Null JIRA Keys

For API tests without JIRA keys:
- System falls back to `testCaseId` as the unique identifier
- A warning is logged: "Using testCaseId as fallback"
- The test is still ingested successfully

## Ingestion Methods

### Method 1: Command Line Ingestion

```bash
# Ingest functional tests
python -m src.ingest.ingest_functional data/functional_tests_xray.json

# Ingest API tests
python -m src.ingest.ingest_api data/api_tests_xray.json

# Or use the Makefile (ingests both)
make ingest
```

### Method 2: API Endpoint

```bash
# Trigger ingestion via API
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "functional_path": "data/functional_tests_xray.json",
    "api_path": "data/api_tests_xray.json"
  }'
```

### Method 3: MCP Tool (for AI Assistants)

```
"Ingest the functional tests from data/functional_tests_xray.json"
```

## Field Harmonization

The system automatically harmonizes fields between formats:

| Functional Format | API Format | Normalized Field |
|-------------------|------------|------------------|
| `labels` | `tags` | `tags` |
| `folder` | `folderStructure` | `folderStructure` |
| `issueKey` | `jiraKey` | `jiraKey` |
| `summary` | `title` | `title` |
| `testScript.steps` | `steps` | `steps` |

### Automatic Conversions

1. **Folder Structure**:
   - String paths are split: `"/Web/Team"` → `["Web", "Team"]`
   - Arrays are preserved as-is

2. **Step Processing**:
   - Functional: Combines `action`, `data`, and `result`
   - API: Uses `action` and `expected` array

3. **Missing Fields**:
   - Default priority: "Medium"
   - Empty arrays for missing tags/platforms
   - Current timestamp for `updatedAt`

## Step-by-Step Ingestion

### Step 1: Prepare Your Data

1. **Validate JSON structure**:
   ```bash
   # Check if JSON is valid
   python -m json.tool data/your_tests.json > /dev/null
   ```

2. **Verify required fields**:
   - Functional: `issueKey` or `issueId`
   - API: `jiraKey` or `testCaseId`
   - Both: `title/summary` and `steps`

### Step 2: Start Services

```bash
# Start everything
make dev

# Or start services separately
make qdrant-up
make api-dev
```

### Step 3: Initialize Collections

```bash
# Run only once (idempotent)
python -m src.models.schema
```

### Step 4: Run Ingestion

```bash
# For functional tests
python -m src.ingest.ingest_functional data/functional_tests_xray.json

# Expected output:
# Starting ingestion of functional tests...
# Loaded 150 tests from data/functional_tests_xray.json
# Processing batch 1/3 (50 tests)...
# [Progress bars and statistics]
# Ingestion complete!
```

### Step 5: Verify Ingestion

```bash
# Check collection statistics
curl http://localhost:8000/healthz | jq

# Search for ingested tests
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "team page", "top_k": 5}' | jq
```

## Validation and Monitoring

### Pre-Ingestion Validation

The system validates:
- ✓ JSON structure and syntax
- ✓ Required fields presence
- ✓ Data type correctness
- ✓ Step index uniqueness

### During Ingestion

Monitor progress via:
- Progress bars for each batch
- Real-time statistics (docs/sec, vectors/sec)
- Warning messages for issues
- Error logs for failures

### Post-Ingestion Verification

```python
# Check specific test
curl http://localhost:8000/by-jira/FRAMED-1390

# Get collection stats
curl http://localhost:6533/collections/test_docs

# Count total documents
curl http://localhost:6533/collections/test_docs/points/count
```

## Troubleshooting

### Common Issues

#### 1. "Collection does not exist"
```bash
# Solution: Create collections
python -m src.models.schema
```

#### 2. "OpenAI API key not found"
```bash
# Solution: Set API key in .env
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

#### 3. "Duplicate UID" warnings
- Normal behavior - system updates existing tests
- Old vectors are deleted before inserting new ones

#### 4. "Using testCaseId as fallback"
- Warning for API tests without JIRA keys
- Test is still ingested using testCaseId as UID

#### 5. Slow ingestion
```bash
# Increase batch size (default: 50)
BATCH_SIZE=100 python -m src.ingest.ingest_functional data/tests.json
```

### Debug Mode

Enable detailed logging:
```bash
LOG_LEVEL=DEBUG python -m src.ingest.ingest_functional data/tests.json
```

## Best Practices

### 1. Data Preparation

- **Validate JSON** before ingestion
- **Remove duplicates** at source
- **Ensure consistent** field naming
- **Backup original** data files

### 2. Batch Processing

- Default batch size: 50 (optimal for most cases)
- Increase for better throughput on large datasets
- Decrease if hitting rate limits

### 3. Incremental Updates

```python
# Re-ingestion is safe - system handles updates
# Old data is replaced, not duplicated
python -m src.ingest.ingest_api updated_tests.json
```

### 4. Performance Optimization

- **Embedding Cache**: Reuse embeddings for identical text
- **Batch API Calls**: Process multiple texts per request
- **Async Processing**: Overlap I/O operations

### 5. Monitoring

```bash
# Watch logs during ingestion
tail -f logs/ingestion.log

# Monitor Qdrant metrics
curl http://localhost:6533/metrics
```

## Advanced Topics

### Custom Field Mapping

Modify `src/ingest/normalize.py` to add custom field mappings:

```python
# Add custom field mapping
if "customField" in test_data:
    normalized["customField"] = test_data["customField"]
```

### Filtering During Ingestion

```python
# Example: Only ingest high-priority tests
tests = [t for t in tests if t.get("priority") == "High"]
```

### Embedding Optimization

```python
# Use smaller model for faster ingestion
EMBED_MODEL=text-embedding-3-small python -m src.ingest.ingest_api data/tests.json
```

### Parallel Ingestion

For very large datasets:
```bash
# Split file and run parallel processes
split -l 1000 data/large_tests.json chunk_
ls chunk_* | xargs -P 4 -I {} python -m src.ingest.ingest_api {}
```

## Summary Checklist

- [ ] Services running (Qdrant + API)
- [ ] Collections created
- [ ] API key configured
- [ ] JSON data validated
- [ ] Ingestion script executed
- [ ] Results verified via search

For additional help, see:
- [API Documentation](../README.md#api-endpoints)
- [Search Guide](SEARCH_GUIDE.md)
- [Troubleshooting](../README.md#troubleshooting)