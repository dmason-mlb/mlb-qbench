"""Ingest functional test data from JSON into Qdrant."""

import json
import sys
import uuid
from typing import Any, Optional

import structlog
from dotenv import load_dotenv
from qdrant_client.models import FieldCondition, Filter, MatchValue, PointStruct

from ..counter_service import get_test_id_counter
from ..embedder import combine_test_fields_for_embedding, get_embedder
from ..models.schema import TEST_DOCS_COLLECTION, TEST_STEPS_COLLECTION, get_client
from ..models.test_models import TestDoc
from .normalize import normalize_test_batch

logger = structlog.get_logger()


def load_functional_tests(file_path: str) -> list[dict[str, Any]]:
    """Load functional tests from JSON file."""
    try:
        with open(file_path, encoding='utf-8') as f:
            data = json.load(f)

        # Handle different possible structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # Check for Xray format with info and tests structure
            if 'info' in data and 'tests' in data:
                logger.info(f"Found Xray format with {len(data['tests'])} tests")
                return data['tests']
            # Check for common wrapper keys
            elif 'rows' in data:
                return data['rows']
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
        logger.error(f"Error loading functional tests: {e}")
        return []


async def create_points_from_test(test_doc: TestDoc, embedder, test_id: Optional[int] = None) -> tuple[PointStruct, list[PointStruct]]:
    """Create Qdrant points from a test document."""
    # Generate document-level embedding
    doc_text = combine_test_fields_for_embedding(test_doc.model_dump())
    doc_embedding = await embedder.embed(doc_text)
    
    # Use provided test_id or get from test_doc
    if test_id is None:
        test_id = test_doc.testId
        if test_id is None:
            # This shouldn't happen in new code but handle for safety
            counter = get_test_id_counter()
            test_id = counter.get_next_id()

    # Create document point
    doc_point = PointStruct(
        id=str(uuid.uuid4()),
        vector=doc_embedding,
        payload={
            "testId": test_id,
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
        step_embedding = await embedder.embed(step_text)

        step_point = PointStruct(
            id=str(uuid.uuid4()),
            vector=step_embedding,
            payload={
                "parent_test_id": test_id,
                "parent_uid": test_doc.uid,  # Keep for backward compatibility
                "step_index": step.index,
                "action": step.action,
                "expected": step.expected
            }
        )
        step_points.append(step_point)

    return doc_point, step_points


async def create_points_from_test_batch(test_docs: list[TestDoc], embedder, embed_batch_size: int = 25, test_ids: Optional[list[int]] = None) -> tuple[list[PointStruct], list[PointStruct]]:
    """Create Qdrant points from a batch of test documents with efficient batch embedding."""
    import asyncio
    
    # Get test IDs if not provided
    if test_ids is None:
        counter = get_test_id_counter()
        # Reserve a range of IDs for this batch
        start_id, end_id = counter.reserve_range(len(test_docs))
        test_ids = list(range(start_id, end_id + 1))
    
    # Assign test IDs to documents
    for test_doc, test_id in zip(test_docs, test_ids):
        test_doc.testId = test_id

    # Prepare all texts for batch embedding
    doc_texts = []
    step_texts = []
    doc_metadata = []
    step_metadata = []

    # Collect all document texts
    for test_doc in test_docs:
        doc_text = combine_test_fields_for_embedding(test_doc.model_dump())
        doc_texts.append(doc_text)
        doc_metadata.append(test_doc)

    # Collect all step texts
    for test_doc in test_docs:
        for step in test_doc.steps:
            step_text = f"{step.action} Expected: {', '.join(step.expected)}"
            step_texts.append(step_text)
            step_metadata.append((test_doc.testId, test_doc.uid, step))

    # Batch embed all texts concurrently
    embed_tasks = []

    # Split document texts into batches
    for i in range(0, len(doc_texts), embed_batch_size):
        batch = doc_texts[i:i + embed_batch_size]
        if batch:
            embed_tasks.append(('docs', i // embed_batch_size, embedder.embed(batch)))

    # Split step texts into batches
    for i in range(0, len(step_texts), embed_batch_size):
        batch = step_texts[i:i + embed_batch_size]
        if batch:
            embed_tasks.append(('steps', i // embed_batch_size, embedder.embed(batch)))

    # Execute all embedding requests concurrently
    if embed_tasks:
        task_info, embedding_results = zip(*[(task[:-1], task[-1]) for task in embed_tasks])
        embeddings_list = await asyncio.gather(*embedding_results, return_exceptions=True)

        # Process embedding results
        doc_embeddings = []
        step_embeddings = []

        for (embed_type, batch_idx), embeddings in zip(task_info, embeddings_list):
            if isinstance(embeddings, Exception):
                logger.error(f"Batch embedding failed for {embed_type} batch {batch_idx}: {embeddings}")
                raise embeddings

            if embed_type == 'docs':
                doc_embeddings.extend(embeddings)
            elif embed_type == 'steps':
                step_embeddings.extend(embeddings)
    else:
        doc_embeddings = []
        step_embeddings = []

    # Create document points
    doc_points = []
    for test_doc, doc_embedding in zip(doc_metadata, doc_embeddings):
        doc_point = PointStruct(
            id=str(uuid.uuid4()),
            vector=doc_embedding,
            payload={
                "testId": test_doc.testId,
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
        doc_points.append(doc_point)

    # Create step points
    step_points = []
    for (parent_test_id, parent_uid, step), step_embedding in zip(step_metadata, step_embeddings):
        step_point = PointStruct(
            id=str(uuid.uuid4()),
            vector=step_embedding,
            payload={
                "parent_test_id": parent_test_id,
                "parent_uid": parent_uid,  # Keep for backward compatibility
                "step_index": step.index,
                "action": step.action,
                "expected": step.expected
            }
        )
        step_points.append(step_point)

    return doc_points, step_points


async def ingest_functional_tests(
    file_path: str,
    batch_size: int = 50,
    recreate: bool = False,
    embedder=None,
    client=None
) -> dict[str, Any]:
    """Ingest functional tests into Qdrant."""
    # Load environment variables
    load_dotenv()

    # Initialize clients (use provided ones or create new ones)
    client = client or get_client()
    embedder = embedder or get_embedder()

    # Load and normalize tests
    logger.info(f"Loading functional tests from {file_path}")
    raw_tests = load_functional_tests(file_path)

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
    normalized_tests, warnings = normalize_test_batch(raw_tests, "functional")
    logger.info(f"Normalized {len(normalized_tests)} tests")

    # Log warnings
    for warning in warnings:
        logger.warning(warning)

    # Check existing UIDs and testIds to enable idempotent updates
    existing_uids = set()
    existing_test_ids = {}  # Map uid to testId
    try:
        # Query for all UIDs and testIds (this is efficient with keyword index)
        scroll_result = client.scroll(
            collection_name=TEST_DOCS_COLLECTION,
            limit=10000,
            with_payload=["uid", "testId"],
            with_vectors=False
        )
        for point in scroll_result[0]:
            uid = point.payload.get("uid")
            test_id = point.payload.get("testId")
            if uid:
                existing_uids.add(uid)
                if test_id is not None:
                    existing_test_ids[uid] = test_id
        logger.info(f"Found {len(existing_uids)} existing tests")
    except Exception as e:
        logger.warning(f"Could not check existing tests: {e}")

    # Process in batches
    doc_points = []
    step_points = []
    processed = 0
    errors = []

    for i in range(0, len(normalized_tests), batch_size):
        batch = normalized_tests[i:i + batch_size]
        logger.info(f"Processing batch {i // batch_size + 1} ({len(batch)} tests)")

        # Separate tests that need updating vs new tests
        update_tests = []
        new_tests = []
        
        # Assign testIds
        for test_doc in batch:
            if test_doc.uid in existing_uids:
                # Preserve existing testId for updates
                test_doc.testId = existing_test_ids.get(test_doc.uid)
                update_tests.append(test_doc)
            else:
                new_tests.append(test_doc)

        # Delete old points for tests being updated
        for test_doc in update_tests:
            try:
                logger.info(f"Updating existing test {test_doc.uid} (testId: {test_doc.testId})")
                # Delete by testId if available, otherwise fall back to uid
                if test_doc.testId is not None:
                    client.delete(
                        collection_name=TEST_DOCS_COLLECTION,
                        points_selector=Filter(
                            must=[FieldCondition(key="testId", match=MatchValue(value=test_doc.testId))]
                        )
                    )
                    client.delete(
                        collection_name=TEST_STEPS_COLLECTION,
                        points_selector=Filter(
                            must=[FieldCondition(key="parent_test_id", match=MatchValue(value=test_doc.testId))]
                        )
                    )
                else:
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
            except Exception as e:
                error_msg = f"Error deleting old points for test {test_doc.uid}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Process all tests in batch (both new and updated)
        try:
            if batch:
                batch_doc_points, batch_step_points = await create_points_from_test_batch(
                    batch, embedder, embed_batch_size=25
                )
                doc_points.extend(batch_doc_points)
                step_points.extend(batch_step_points)
                processed += len(batch)

                logger.info(f"Batch processed: {len(batch_doc_points)} docs, {len(batch_step_points)} steps")

        except Exception as e:
            error_msg = f"Error processing batch {i // batch_size + 1}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            # Continue with next batch instead of failing completely

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
        file_path = "data/functional_tests_xray.json"

    # Run ingestion
    import asyncio
    result = asyncio.run(ingest_functional_tests(file_path))

    # Print summary
    print("\nIngestion Summary:")
    print(f"  Status: {result['status']}")
    print(f"  Ingested: {result['ingested']}/{result['total']} tests")
    print(f"  Warnings: {len(result['warnings'])}")
    print(f"  Errors: {len(result['errors'])}")

    if result['errors']:
        print("\nErrors:")
        for error in result['errors'][:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(result['errors']) > 5:
            print(f"  ... and {len(result['errors']) - 5} more errors")
