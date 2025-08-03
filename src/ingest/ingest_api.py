"""Ingest API test data from JSON into Qdrant."""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import structlog
from dotenv import load_dotenv
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import uuid

from ..models.schema import get_client, TEST_DOCS_COLLECTION, TEST_STEPS_COLLECTION
from ..models.test_models import TestDoc
from ..embedder import get_embedder, combine_test_fields_for_embedding
from .normalize import normalize_api_test, normalize_test_batch

logger = structlog.get_logger()


def load_api_tests(file_path: str) -> List[Dict[str, Any]]:
    """Load API tests from JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different possible structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Check for Xray format with testSuite wrapper
            if 'testSuite' in data and 'testCases' in data['testSuite']:
                logger.info(f"Found Xray format with {len(data['testSuite']['testCases'])} test cases")
                return data['testSuite']['testCases']
            # Check for common wrapper keys
            elif 'tests' in data:
                return data['tests']
            elif 'data' in data:
                return data['data']
            else:
                # Single test object
                return [data]
        else:
            logger.error(f"Unexpected data structure in {file_path}")
            return []
            
    except Exception as e:
        logger.error(f"Error loading API tests: {e}")
        return []


def create_points_from_test(test_doc: TestDoc, embedder) -> tuple[PointStruct, List[PointStruct]]:
    """Create Qdrant points from a test document."""
    # Generate document-level embedding
    doc_text = combine_test_fields_for_embedding(test_doc.dict())
    doc_embedding = embedder.embed(doc_text)
    
    # Create document point
    doc_point = PointStruct(
        id=str(uuid.uuid4()),
        vector=doc_embedding,
        payload={
            "uid": test_doc.uid,
            "jiraKey": test_doc.jiraKey,
            "testCaseId": test_doc.testCaseId,
            "title": test_doc.title,
            "summary": test_doc.summary,
            "description": test_doc.description,
            "testType": test_doc.testType,
            "priority": test_doc.priority,
            "platforms": test_doc.platforms,
            "tags": test_doc.tags,
            "folderStructure": test_doc.folderStructure,
            "preconditions": test_doc.preconditions,
            "expectedResults": test_doc.expectedResults,
            "testData": test_doc.testData,
            "relatedIssues": test_doc.relatedIssues,
            "testPath": test_doc.testPath,
            "source": test_doc.source,
            "ingested_at": test_doc.ingested_at.isoformat(),
            "step_count": len(test_doc.steps)
        }
    )
    
    # Create step points
    step_points = []
    for step in test_doc.steps:
        step_text = f"{step.action} Expected: {', '.join(step.expected)}"
        step_embedding = embedder.embed(step_text)
        
        step_point = PointStruct(
            id=str(uuid.uuid4()),
            vector=step_embedding,
            payload={
                "parent_uid": test_doc.uid,
                "step_index": step.index,
                "action": step.action,
                "expected": step.expected
            }
        )
        step_points.append(step_point)
    
    return doc_point, step_points


def ingest_api_tests(
    file_path: str,
    batch_size: int = 50,
    recreate: bool = False
) -> Dict[str, Any]:
    """Ingest API tests into Qdrant."""
    # Load environment variables
    load_dotenv()
    
    # Initialize clients
    client = get_client()
    embedder = get_embedder()
    
    # Load and normalize tests
    logger.info(f"Loading API tests from {file_path}")
    raw_tests = load_api_tests(file_path)
    
    if not raw_tests:
        return {
            "status": "error",
            "message": "No tests found in file",
            "ingested": 0,
            "total": 0,
            "warnings": [],
            "errors": ["No tests found in file"]
        }
    
    logger.info(f"Found {len(raw_tests)} tests to process")
    
    # Normalize tests
    normalized_tests, warnings = normalize_test_batch(raw_tests, "api")
    logger.info(f"Normalized {len(normalized_tests)} tests")
    
    # Log warnings
    for warning in warnings:
        logger.warning(warning)
    
    # Check existing UIDs to enable idempotent updates
    existing_uids = set()
    try:
        # Query for all UIDs (this is efficient with keyword index)
        scroll_result = client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            limit=10000,
            with_payload=["uid"],
            with_vectors=False
        )
        existing_uids = {point.payload["uid"] for point in scroll_result[0]}
        logger.info(f"Found {len(existing_uids)} existing tests")
    except Exception as e:
        logger.warning(f"Could not check existing tests: {e}")
    
    # Process in batches
    doc_points = []
    step_points = []
    processed = 0
    errors = []
    updated = 0
    
    for i in range(0, len(normalized_tests), batch_size):
        batch = normalized_tests[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1}")
        
        for test_doc in batch:
            try:
                # Skip if already exists and not updating
                if test_doc.uid in existing_uids:
                    logger.info(f"Updating existing test {test_doc.uid}")
                    updated += 1
                    # Delete old points first
                    client.delete(
                        collection_name=TEST_DOCS_COLLECTION,
                        points_selector=Filter(
                            must=[FieldCondition(key="uid", match=MatchValue(value=test_doc.uid))]
                        )
                    )
                    client.delete(
                        collection_name=TEST_STEPS_COLLECTION,
                        points_selector=Filter(
                            must=[FieldCondition(key="parent_uid", match=MatchValue(value=test_doc.uid))]
                        )
                    )
                
                # Create new points
                doc_point, test_step_points = create_points_from_test(test_doc, embedder)
                doc_points.append(doc_point)
                step_points.extend(test_step_points)
                processed += 1
                
            except Exception as e:
                error_msg = f"Error processing test {test_doc.uid}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Upsert batch to Qdrant
        if doc_points:
            try:
                client.upsert(
                    collection_name=TEST_DOCS_COLLECTION,
                    points=doc_points
                )
                logger.info(f"Upserted {len(doc_points)} documents")
                doc_points = []  # Clear for next batch
            except Exception as e:
                logger.error(f"Error upserting documents: {e}")
                errors.append(f"Document upsert error: {str(e)}")
        
        if step_points:
            try:
                client.upsert(
                    collection_name=TEST_STEPS_COLLECTION,
                    points=step_points
                )
                logger.info(f"Upserted {len(step_points)} steps")
                step_points = []  # Clear for next batch
            except Exception as e:
                logger.error(f"Error upserting steps: {e}")
                errors.append(f"Step upsert error: {str(e)}")
    
    # Final stats
    result = {
        "status": "success" if processed > 0 else "error",
        "ingested": processed,
        "updated": updated,
        "total": len(raw_tests),
        "normalized": len(normalized_tests),
        "warnings": warnings,
        "errors": errors,
        "embedder_stats": embedder.get_stats()
    }
    
    logger.info("Ingestion complete", result=result)
    return result


if __name__ == "__main__":
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/api_tests_xray.json"
    
    # Run ingestion
    result = ingest_api_tests(file_path)
    
    # Print summary
    print(f"\nIngestion Summary:")
    print(f"  Status: {result['status']}")
    print(f"  Ingested: {result['ingested']}/{result['total']} tests")
    print(f"  Updated: {result.get('updated', 0)} existing tests")
    print(f"  Warnings: {len(result['warnings'])}")
    print(f"  Errors: {len(result['errors'])}")
    
    if result['errors']:
        print("\nErrors:")
        for error in result['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(result['errors']) > 5:
            print(f"  ... and {len(result['errors']) - 5} more errors")