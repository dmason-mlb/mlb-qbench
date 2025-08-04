"""Global test configuration and fixtures."""

import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from qdrant_client import QdrantClient

# Ensure test modules can import src
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "QDRANT_URL": "http://localhost:6533",
        "EMBED_PROVIDER": "openai",
        "EMBED_MODEL": "text-embedding-3-large",
        "OPENAI_API_KEY": "test-openai-key",
        "MASTER_API_KEY": "test-master-key",
        "API_KEYS": "test-key-1,test-key-2",
    }
    
    with patch.dict(os.environ, env_vars, clear=False):
        yield env_vars


@pytest.fixture
def mock_qdrant_client():
    """Mock Qdrant client for testing."""
    mock_client = MagicMock(spec=QdrantClient)
    
    # Mock common methods
    mock_client.get_collections.return_value = MagicMock()
    mock_client.collection_exists.return_value = True
    mock_client.search.return_value = []
    mock_client.scroll.return_value = ([], None)
    mock_client.upsert.return_value = MagicMock()
    mock_client.delete.return_value = MagicMock()
    mock_client.get_collection.return_value = MagicMock()
    
    return mock_client


@pytest.fixture
def mock_async_qdrant_client():
    """Mock async Qdrant client for testing."""
    mock_client = AsyncMock()
    
    # Mock common async methods
    mock_client.get_collections = AsyncMock(return_value=MagicMock())
    mock_client.collection_exists = AsyncMock(return_value=True)
    mock_client.search = AsyncMock(return_value=[])
    mock_client.scroll = AsyncMock(return_value=([], None))
    mock_client.upsert = AsyncMock(return_value=MagicMock())
    mock_client.delete = AsyncMock(return_value=MagicMock())
    mock_client.get_collection = AsyncMock(return_value=MagicMock())
    
    return mock_client


@pytest.fixture
def mock_embedding_provider():
    """Mock embedding provider for testing."""
    mock_embedder = MagicMock()
    mock_embedder.embed.return_value = [[0.1] * 3072]  # Mock 3072-dim embedding
    mock_embedder.embed_batch.return_value = [[[0.1] * 3072], [[0.2] * 3072]]
    mock_embedder.get_dimension.return_value = 3072
    return mock_embedder


@pytest.fixture
def mock_async_embedding_provider():
    """Mock async embedding provider for testing."""
    mock_embedder = AsyncMock()
    mock_embedder.embed = AsyncMock(return_value=[0.1] * 3072)  # Single embedding
    mock_embedder.embed_batch = AsyncMock(return_value=[[[0.1] * 3072], [[0.2] * 3072]])
    mock_embedder.get_dimension = AsyncMock(return_value=3072)
    mock_embedder.get_stats = MagicMock(return_value={
        "provider": "MockEmbedder",
        "model": "test-model",
        "embed_count": 0,
        "total_tokens": 0
    })
    mock_embedder.close = AsyncMock()
    return mock_embedder


@pytest.fixture
def sample_test_data():
    """Sample test data for testing."""
    return {
        "functional": {
            "issueKey": "FRAMED-1234",
            "testCaseId": "tc_func_1234",
            "summary": "Sample functional test",
            "labels": ["web", "login"],
            "priority": "High",
            "folder": "/Web/Authentication",
            "platforms": ["web"],
            "testScript": {
                "steps": [
                    {
                        "index": 1,
                        "action": "Navigate to login page",
                        "result": "Login page is displayed"
                    },
                    {
                        "index": 2,
                        "action": "Enter valid credentials",
                        "result": "User is logged in successfully"
                    }
                ]
            }
        },
        "api": {
            "jiraKey": "API-5678",
            "testCaseId": "tc_api_5678",
            "title": "Sample API test",
            "testType": "API",
            "priority": "Medium",
            "platforms": ["api"],
            "folderStructure": "API/Authentication",
            "tags": ["api", "auth"],
            "steps": [
                {
                    "action": "POST /api/login with valid credentials",
                    "expected": ["200 OK", "JWT token returned"]
                }
            ]
        }
    }


@pytest.fixture
def mock_container(mock_qdrant_client, mock_async_embedding_provider):
    """Mock dependency injection container for testing."""
    from src.container import Container
    
    container = Container()
    
    # Register mocked services
    container.register_instance('qdrant_client', mock_qdrant_client)
    container.register_instance('embedder', mock_async_embedding_provider)
    
    # Mock validators
    mock_path_validator = MagicMock()
    mock_path_validator.return_value = MagicMock()
    mock_path_validator.return_value.exists.return_value = True
    container.register_instance('path_validator', mock_path_validator)
    
    mock_jira_validator = MagicMock()
    mock_jira_validator.return_value = "TEST-123"  # Valid JIRA key
    container.register_instance('jira_validator', mock_jira_validator)
    
    # Mock rate limiter
    mock_rate_limiter = MagicMock()
    mock_rate_limiter.limit.return_value = lambda f: f  # Passthrough decorator
    container.register_instance('rate_limiter', mock_rate_limiter)
    
    return container


@pytest.fixture
def mock_fastapi_app():
    """Mock FastAPI app for testing without running server."""
    # This will be set up when we create service tests
    pass


class AsyncContextManager:
    """Helper class for async context manager testing."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def async_context_manager():
    """Helper fixture for async context managers."""
    return AsyncContextManager


# Common test utilities
class TestHelpers:
    """Common test helper methods."""
    
    @staticmethod
    def create_mock_search_result(uid: str, score: float = 0.8):
        """Create a mock search result."""
        return MagicMock(
            id=uid,
            score=score,
            payload={
                "uid": uid,
                "jiraKey": f"TEST-{uid}",
                "title": f"Test {uid}",
                "testType": "Functional",
                "priority": "Medium"
            }
        )
    
    @staticmethod
    def create_mock_test_document(uid: str = "test-123"):
        """Create a mock test document."""
        return {
            "uid": uid,
            "jiraKey": f"TEST-{uid}",
            "testCaseId": f"tc_{uid}",
            "title": f"Sample test {uid}",
            "summary": f"Summary for {uid}",
            "testType": "Functional",
            "priority": "Medium",
            "platforms": ["web"],
            "tags": ["test"],
            "folderStructure": "/Test/Sample",
            "steps": [
                {
                    "stepNumber": 1,
                    "action": f"Action for {uid}",
                    "expected": [f"Expected result for {uid}"]
                }
            ]
        }


@pytest.fixture
def test_helpers():
    """Test helper methods fixture."""
    return TestHelpers