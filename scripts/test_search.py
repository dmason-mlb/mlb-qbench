#!/usr/bin/env python3
"""Test search functionality with example queries."""

import requests
import json
import sys
from typing import Dict, Any, List

# API base URL
BASE_URL = "http://localhost:8000"


def pretty_print_result(result: Dict[str, Any]) -> None:
    """Pretty print a search result."""
    test = result["test"]
    print(f"\n{'='*60}")
    print(f"Title: {test['title']}")
    print(f"UID: {test['uid']} | Priority: {test['priority']}")
    print(f"Tags: {', '.join(test.get('tags', []))}")
    print(f"Score: {result['score']:.3f}")
    
    if result.get("matched_steps"):
        print(f"Matched Steps: {result['matched_steps']}")
    
    if test.get("summary"):
        print(f"\nSummary: {test['summary']}")


def test_search(query: str, filters: Dict[str, Any] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """Test search endpoint."""
    print(f"\n🔍 Searching for: '{query}'")
    if filters:
        print(f"   Filters: {filters}")
    
    payload = {
        "query": query,
        "top_k": top_k
    }
    if filters:
        payload["filters"] = filters
    
    try:
        response = requests.post(f"{BASE_URL}/search", json=payload)
        response.raise_for_status()
        
        results = response.json()
        print(f"   Found {len(results)} results")
        
        for result in results:
            pretty_print_result(result)
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Search failed: {e}")
        return []


def test_health() -> bool:
    """Test health endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/healthz")
        response.raise_for_status()
        
        health = response.json()
        print(f"\n✅ Health Check: {health['status']}")
        
        # Print collection stats
        if "qdrant" in health and "collections" in health["qdrant"]:
            for coll_name, coll_info in health["qdrant"]["collections"].items():
                if isinstance(coll_info, dict) and "points_count" in coll_info:
                    print(f"   {coll_name}: {coll_info['points_count']} points")
        
        return health["status"] == "healthy"
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_by_jira(jira_key: str) -> Dict[str, Any]:
    """Test get by JIRA endpoint."""
    print(f"\n📋 Getting test by JIRA key: {jira_key}")
    
    try:
        response = requests.get(f"{BASE_URL}/by-jira/{jira_key}")
        response.raise_for_status()
        
        test = response.json()
        print(f"   Found: {test['title']}")
        return test
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Get by JIRA failed: {e}")
        return {}


def test_similar(jira_key: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Test similar endpoint."""
    print(f"\n🔗 Finding tests similar to: {jira_key}")
    
    try:
        response = requests.get(f"{BASE_URL}/similar/{jira_key}?top_k={top_k}")
        response.raise_for_status()
        
        results = response.json()
        print(f"   Found {len(results)} similar tests")
        
        for result in results[:3]:  # Show top 3
            test = result["test"]
            print(f"   - {test['title']} (score: {result['score']:.3f})")
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Find similar failed: {e}")
        return []


def main():
    """Run test queries."""
    print("MLB QBench Search Tests")
    print("=" * 80)
    
    # Check health first
    if not test_health():
        print("\n⚠️  API is not healthy. Make sure the service is running.")
        sys.exit(1)
    
    # Test queries from requirements
    test_queries = [
        {
            "query": "Spanish localization on Team Page",
            "description": "Should find both API and functional tests with localization tags"
        },
        {
            "query": "Live game MIG validations",
            "description": "Should match tests with live_state and requires_live_game tags"
        },
        {
            "query": "Jewel event regressions",
            "description": "Should find both document and step hits with jewel_event"
        }
    ]
    
    # Run test queries
    for test in test_queries:
        print(f"\n{'='*80}")
        print(f"Test: {test['description']}")
        test_search(test["query"])
    
    # Test with filters
    print(f"\n{'='*80}")
    print("Test: Search with filters")
    test_search(
        "team page",
        filters={"priority": "High", "tags": ["api"]}
    )
    
    # Test other endpoints (if we have data)
    print(f"\n{'='*80}")
    print("Test: Other endpoints")
    
    # Try to get a known test
    test_jira_keys = ["FRAMED-1390", "FRAMED-643", "API-001"]
    for jira_key in test_jira_keys:
        test_doc = test_by_jira(jira_key)
        if test_doc:
            # Found one, test similar
            test_similar(jira_key, top_k=3)
            break
    
    print(f"\n{'='*80}")
    print("✅ All tests completed!")


if __name__ == "__main__":
    main()