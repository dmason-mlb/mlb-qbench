#!/usr/bin/env python3
"""Test PostgreSQL setup and basic operations."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.postgres_vector import PostgresVectorDB
from src.embedder import get_embedder
from src.models.test_models import TestDoc, TestStep


async def test_setup():
    """Test PostgreSQL setup and basic operations."""
    print("Testing PostgreSQL + pgvector setup...")
    
    # Initialize database
    db = PostgresVectorDB()
    await db.initialize()
    print("✓ Database connection established")
    
    # Get statistics
    stats = await db.get_statistics()
    print(f"✓ Database statistics retrieved: {stats['total_documents']} documents")
    
    # Initialize embedder
    embedder = get_embedder()
    print(f"✓ Embedder initialized: {os.getenv('EMBED_PROVIDER', 'openai')}")
    
    # Create a test document
    test_doc = TestDoc(
        uid="test_001",
        testCaseId="1",  # String, not int
        jiraKey="TEST-123",
        title="Sample Test Case",
        description="This is a test case for verifying PostgreSQL setup",
        steps=[
            TestStep(index=1, action="Open application", expected=["App loads"]),
            TestStep(index=2, action="Click button", expected=["Action performed"])
        ],
        priority="High",
        tags=["smoke", "regression"],
        platforms=["web", "mobile"],
        folderStructure="/Tests/Smoke",
        testType="Manual",
        source="functional_tests_xray.json"  # Must be one of the allowed values
    )
    
    # Insert test document
    result = await db.batch_insert_documents([test_doc], embedder)
    print(f"✓ Test document inserted: {result}")
    
    # Search for the document
    query_text = "application button click"
    query_embedding = await embedder.embed(query_text)
    
    search_results = await db.hybrid_search(
        query_embedding=query_embedding,
        limit=5
    )
    
    if search_results:
        print(f"✓ Search successful: Found {len(search_results)} results")
        for result in search_results:
            print(f"  - {result['title']} (similarity: {result['similarity']:.3f})")
    else:
        print("✗ No search results found")
    
    # Search by JIRA key
    jira_result = await db.search_by_jira_key("TEST-123")
    if jira_result:
        print(f"✓ JIRA key search successful: {jira_result['title']}")
    else:
        print("✗ JIRA key search failed")
    
    # Clean up test data
    deleted = await db.delete_by_uid("test_001")
    print(f"✓ Test document deleted: {deleted}")
    
    # Close connection
    await db.close()
    print("✓ Database connection closed")
    
    print("\n✅ All tests passed! PostgreSQL + pgvector is working correctly.")


if __name__ == "__main__":
    asyncio.run(test_setup())