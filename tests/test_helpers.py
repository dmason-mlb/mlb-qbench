"""Test helper utilities and async testing patterns."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from qdrant_client.models import Distance, PointStruct, ScoredPoint, VectorParams


class AsyncTestCase:
    """Base class for async test cases with common patterns."""
    
    def setup_method(self):
        """Setup method called before each test method."""
        pass
    
    def teardown_method(self):
        """Teardown method called after each test method."""
        pass
    
    @pytest.fixture(autouse=True)
    async def async_setup_teardown(self):
        """Async setup and teardown fixture."""
        await self.async_setup()
        yield
        await self.async_teardown()
    
    async def async_setup(self):
        """Async setup method - override in subclasses."""
        pass
    
    async def async_teardown(self):
        """Async teardown method - override in subclasses."""
        pass


class MockQdrantResponses:
    """Factory for creating mock Qdrant responses."""
    
    @staticmethod
    def create_search_response(
        results: List[Dict[str, Any]], 
        collection_name: str = "test_docs"
    ) -> List[ScoredPoint]:
        """Create a mock search response."""
        scored_points = []
        for i, result in enumerate(results):
            point = ScoredPoint(
                id=result.get("uid", f"test-{i}"),
                score=result.get("score", 0.8),
                payload=result,
                version=1
            )
            scored_points.append(point)
        return scored_points
    
    @staticmethod
    def create_scroll_response(
        results: List[Dict[str, Any]], 
        next_page_offset: Optional[str] = None
    ) -> tuple:
        """Create a mock scroll response."""
        points = []
        for i, result in enumerate(results):
            point = PointStruct(
                id=result.get("uid", f"test-{i}"),
                payload=result,
                vector=result.get("vector", [0.1] * 3072)
            )
            points.append(point)
        return points, next_page_offset
    
    @staticmethod
    def create_collection_info(collection_name: str = "test_docs"):
        """Create a mock collection info response."""
        return MagicMock(
            name=collection_name,
            status="green",
            vectors_count=1000,
            indexed_vectors_count=1000,
            points_count=1000,
            segments_count=1,
            config=MagicMock(
                params=MagicMock(
                    vectors=MagicMock(
                        size=3072,
                        distance=Distance.COSINE
                    )
                )
            )
        )


class MockEmbeddingResponses:
    """Factory for creating mock embedding responses."""
    
    @staticmethod
    def create_embedding_response(
        texts: List[str], 
        dimension: int = 3072
    ) -> List[List[float]]:
        """Create mock embeddings for given texts."""
        embeddings = []
        for i, text in enumerate(texts):
            # Create deterministic embeddings based on text hash for consistency
            hash_val = hash(text) % 1000
            embedding = [(hash_val + j) / 1000.0 for j in range(dimension)]
            embeddings.append(embedding)
        return embeddings
    
    @staticmethod
    def create_openai_response(texts: List[str]) -> MagicMock:
        """Create mock OpenAI API response."""
        embeddings = MockEmbeddingResponses.create_embedding_response(texts)
        
        data = []
        for i, embedding in enumerate(embeddings):
            data.append(MagicMock(
                embedding=embedding,
                index=i
            ))
        
        return MagicMock(
            data=data,
            model="text-embedding-3-large",
            usage=MagicMock(
                prompt_tokens=sum(len(text.split()) for text in texts),
                total_tokens=sum(len(text.split()) for text in texts)
            )
        )


class AsyncPatcher:
    """Utility class for patching async methods in tests."""
    
    def __init__(self):
        self.patches = []
    
    def patch_async_method(
        self, 
        target: str, 
        return_value: Any = None,
        side_effect: Any = None
    ) -> AsyncMock:
        """Patch an async method with AsyncMock."""
        mock = AsyncMock()
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        
        patcher = patch(target, mock)
        self.patches.append(patcher)
        return mock
    
    def start_all(self):
        """Start all patches."""
        for patcher in self.patches:
            patcher.start()
    
    def stop_all(self):
        """Stop all patches."""
        for patcher in self.patches:
            try:
                patcher.stop()
            except RuntimeError:
                # Patch was already stopped
                pass
    
    def __enter__(self):
        self.start_all()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_all()


class AsyncTestClient:
    """Async test client wrapper for FastAPI testing."""
    
    def __init__(self, app):
        self.app = app
        self._client = None
    
    async def __aenter__(self):
        from httpx import AsyncClient
        self._client = AsyncClient(app=self.app, base_url="http://test")
        return self._client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()


@asynccontextmanager
async def async_test_client(app) -> AsyncGenerator[Any, None]:
    """Create an async test client for FastAPI app."""
    async with AsyncTestClient(app) as client:
        yield client


class PerformanceTimer:
    """Timer for measuring async operation performance."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    async def __aenter__(self):
        import time
        self.start_time = time.perf_counter()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        import time
        self.end_time = time.perf_counter()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return self.end_time - self.start_time


def async_timeout(seconds: float):
    """Decorator to timeout async tests."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
        return wrapper
    return decorator


def parametrize_async(*args, **kwargs):
    """Wrapper for pytest.mark.parametrize that works with async tests."""
    return pytest.mark.parametrize(*args, **kwargs)


class MockAsyncContext:
    """Mock async context manager for testing."""
    
    def __init__(self, return_value=None, side_effect=None):
        self.return_value = return_value
        self.side_effect = side_effect
        self.entered = False
        self.exited = False
    
    async def __aenter__(self):
        self.entered = True
        if self.side_effect:
            if isinstance(self.side_effect, Exception):
                raise self.side_effect
            elif callable(self.side_effect):
                return await self.side_effect()
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exited = True
        return False


def create_async_mock_with_spec(spec_class):
    """Create an AsyncMock with proper spec."""
    mock = AsyncMock(spec=spec_class)
    
    # Add common async methods that might be called
    for attr_name in dir(spec_class):
        attr = getattr(spec_class, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            setattr(mock, attr_name, AsyncMock())
    
    return mock


class TestDataBuilder:
    """Builder pattern for creating test data."""
    
    def __init__(self):
        self.data = {}
    
    def with_field(self, key: str, value: Any) -> 'TestDataBuilder':
        """Add a field to the test data."""
        self.data[key] = value
        return self
    
    def with_defaults(self, defaults: Dict[str, Any]) -> 'TestDataBuilder':
        """Set default values for test data."""
        for key, value in defaults.items():
            if key not in self.data:
                self.data[key] = value
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final test data."""
        return self.data.copy()


# Common test data builders
def functional_test_builder() -> TestDataBuilder:
    """Create a builder for functional test data."""
    return TestDataBuilder().with_defaults({
        "issueKey": "FUNC-123",
        "testCaseId": "tc_func_123",
        "summary": "Test summary",
        "labels": ["test"],
        "priority": "Medium",
        "folder": "/Test",
        "platforms": ["web"],
        "testScript": {
            "steps": [
                {
                    "index": 1,
                    "action": "Test action",
                    "result": "Test result"
                }
            ]
        }
    })


def api_test_builder() -> TestDataBuilder:
    """Create a builder for API test data."""
    return TestDataBuilder().with_defaults({
        "jiraKey": "API-123",
        "testCaseId": "tc_api_123",
        "title": "API test",
        "testType": "API",
        "priority": "Medium",
        "platforms": ["api"],
        "folderStructure": "API/Test",
        "tags": ["api"],
        "steps": [
            {
                "action": "API call",
                "expected": ["200 OK"]
            }
        ]
    })


# Export commonly used items
__all__ = [
    'AsyncTestCase',
    'MockQdrantResponses',
    'MockEmbeddingResponses',
    'AsyncPatcher',
    'async_test_client',
    'PerformanceTimer',
    'async_timeout',
    'parametrize_async',
    'MockAsyncContext',
    'create_async_mock_with_spec',
    'TestDataBuilder',
    'functional_test_builder',
    'api_test_builder'
]