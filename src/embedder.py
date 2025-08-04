"""Provider-agnostic embedding wrapper for cloud embedding services."""

import os
import asyncio
from abc import ABC, abstractmethod
from typing import List, Union, Optional, Dict, Any
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tenacity import AsyncRetrying
import structlog
import numpy as np

logger = structlog.get_logger()


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""
    
    def __init__(self, model: str, batch_size: int = 100):
        self.model = model
        self.batch_size = batch_size
        self.embed_count = 0
        self.total_tokens = 0
    
    @abstractmethod
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts. Must be implemented by subclasses."""
        pass
    
    async def embed(self, texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
        """Embed text(s) and return embedding vector(s)."""
        # Handle single text
        if isinstance(texts, str):
            result = (await self._embed_batch([texts]))[0]
            return result
        
        # Handle empty list
        if not texts:
            return []
        
        # Process in batches
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            logger.info(f"Embedding batch {i // self.batch_size + 1}", 
                       batch_size=len(batch), total_texts=len(texts))
            
            batch_embeddings = await self._embed_batch(batch)
            all_embeddings.extend(batch_embeddings)
            self.embed_count += len(batch)
        
        return all_embeddings
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding statistics."""
        return {
            "provider": self.__class__.__name__,
            "model": self.model,
            "embed_count": self.embed_count,
            "total_tokens": self.total_tokens,
        }
    
    async def close(self):
        """Close async resources. Override in subclasses if needed."""
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get embedding provider statistics."""
        return {
            "provider": self.__class__.__name__,
            "model": getattr(self, 'model_name', 'unknown'),
            "embed_count": getattr(self, '_embed_count', 0),
            "total_tokens": getattr(self, '_total_tokens', 0)
        }


class OpenAIEmbedder(EmbeddingProvider):
    """OpenAI embedding provider."""
    
    def __init__(self, model: str = None, batch_size: int = 100):
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        super().__init__(
            model=model or os.getenv("EMBED_MODEL", "text-embedding-3-large"),
            batch_size=batch_size
        )
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.client = AsyncOpenAI(api_key=api_key)
        logger.info(f"Initialized OpenAI embedder with model {self.model}")
    
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts using OpenAI API."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(Exception)
        ):
            with attempt:
                try:
                    response = await self.client.embeddings.create(
                        model=self.model,
                        input=texts,
                        encoding_format="float"
                    )
                    
                    # Track token usage
                    if hasattr(response, 'usage'):
                        self.total_tokens += response.usage.total_tokens
                    
                    # Extract embeddings in order
                    embeddings = [item.embedding for item in response.data]
                    return embeddings
                    
                except Exception as e:
                    logger.error(f"OpenAI embedding error: {e}")
                    raise
    
    async def close(self):
        """Close OpenAI client."""
        await self.client.close()


class CohereEmbedder(EmbeddingProvider):
    """Cohere embedding provider."""
    
    def __init__(self, model: str = None, batch_size: int = 96):
        try:
            import cohere
        except ImportError:
            raise ImportError("cohere package not installed. Run: pip install cohere")
        
        super().__init__(
            model=model or os.getenv("EMBED_MODEL", "embed-english-v3.0"),
            batch_size=batch_size  # Cohere has 96 text limit
        )
        
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable not set")
        
        self.client = cohere.AsyncClient(api_key)
        logger.info(f"Initialized Cohere embedder with model {self.model}")
    
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts using Cohere API."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(Exception)
        ):
            with attempt:
                try:
                    response = await self.client.embed(
                        texts=texts,
                        model=self.model,
                        input_type="search_document",  # Optimized for retrieval
                        truncate="END"  # Truncate from end if too long
                    )
                    
                    # Cohere returns numpy arrays, convert to lists
                    embeddings = [emb.tolist() for emb in response.embeddings]
                    return embeddings
                    
                except Exception as e:
                    logger.error(f"Cohere embedding error: {e}")
                    raise
    
    async def close(self):
        """Close Cohere client."""
        await self.client.close()


class VertexEmbedder(EmbeddingProvider):
    """Google Vertex AI embedding provider."""
    
    def __init__(self, model: str = None, batch_size: int = 250):
        try:
            from google.cloud import aiplatform
            from google.cloud.aiplatform import TextEmbeddingModel
        except ImportError:
            raise ImportError("google-cloud-aiplatform not installed. Run: pip install google-cloud-aiplatform")
        
        super().__init__(
            model=model or os.getenv("EMBED_MODEL", "textembedding-gecko@003"),
            batch_size=batch_size  # Vertex allows up to 250
        )
        
        project_id = os.getenv("VERTEX_PROJECT_ID")
        location = os.getenv("VERTEX_LOCATION", "us-central1")
        
        if not project_id:
            raise ValueError("VERTEX_PROJECT_ID environment variable not set")
        
        aiplatform.init(project=project_id, location=location)
        self.model_client = TextEmbeddingModel.from_pretrained(self.model)
        logger.info(f"Initialized Vertex AI embedder with model {self.model}")
    
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts using Vertex AI."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(Exception)
        ):
            with attempt:
                try:
                    # Run synchronous vertex call in thread pool
                    embeddings = await asyncio.to_thread(
                        self.model_client.get_embeddings, texts
                    )
                    return [emb.values for emb in embeddings]
                    
                except Exception as e:
                    logger.error(f"Vertex AI embedding error: {e}")
                    raise


class AzureEmbedder(EmbeddingProvider):
    """Azure OpenAI embedding provider."""
    
    def __init__(self, model: str = None, batch_size: int = 100):
        try:
            from openai import AsyncAzureOpenAI
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")
        
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        if not deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT_NAME not set")
        
        super().__init__(
            model=model or deployment,
            batch_size=batch_size
        )
        
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-12-01-preview")
        
        if not api_key or not endpoint:
            raise ValueError("Azure OpenAI credentials not set")
        
        self.client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        self.deployment = deployment
        logger.info(f"Initialized Azure OpenAI embedder with deployment {deployment}")
    
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of texts using Azure OpenAI."""
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            retry=retry_if_exception_type(Exception)
        ):
            with attempt:
                try:
                    response = await self.client.embeddings.create(
                        model=self.deployment,
                        input=texts
                    )
                    
                    embeddings = [item.embedding for item in response.data]
                    return embeddings
                    
                except Exception as e:
                    logger.error(f"Azure OpenAI embedding error: {e}")
                    raise
    
    async def close(self):
        """Close Azure OpenAI client."""
        await self.client.close()


def get_embedder(provider: str = None, model: str = None) -> EmbeddingProvider:
    """Factory function to get embedding provider."""
    provider = provider or os.getenv("EMBED_PROVIDER", "openai")
    
    providers = {
        "openai": OpenAIEmbedder,
        "cohere": CohereEmbedder,
        "vertex": VertexEmbedder,
        "azure": AzureEmbedder,
    }
    
    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}. Choose from: {list(providers.keys())}")
    
    return providers[provider](model=model)


# Utility functions for text preparation
def prepare_text_for_embedding(text: str, max_length: int = 8000) -> str:
    """Prepare text for embedding by cleaning and truncating."""
    # Clean whitespace
    text = " ".join(text.split())
    
    # Truncate if needed (leave room for tokenization overhead)
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text


def combine_test_fields_for_embedding(test_data: Dict[str, Any]) -> str:
    """Combine test fields into a single string for doc-level embedding."""
    parts = []
    
    # Title and summary are most important
    if test_data.get("title"):
        parts.append(f"Title: {test_data['title']}")
    
    if test_data.get("summary"):
        parts.append(f"Summary: {test_data['summary']}")
    
    if test_data.get("description"):
        parts.append(f"Description: {test_data['description']}")
    
    # Add tags for semantic richness
    if test_data.get("tags"):
        parts.append(f"Tags: {', '.join(test_data['tags'])}")
    
    # Include test type and priority
    if test_data.get("testType"):
        parts.append(f"Type: {test_data['testType']}")
    
    if test_data.get("priority"):
        parts.append(f"Priority: {test_data['priority']}")
    
    # Add step text
    if test_data.get("steps"):
        step_texts = []
        for step in test_data["steps"]:
            step_text = f"Step {step['index']}: {step['action']}"
            if step.get("expected"):
                step_text += f" Expected: {', '.join(step['expected'])}"
            step_texts.append(step_text)
        parts.append("Steps: " + " ".join(step_texts))
    
    # Combine all parts
    combined = " ".join(parts)
    return prepare_text_for_embedding(combined)


if __name__ == "__main__":
    # Test embedding providers
    import json
    from dotenv import load_dotenv
    
    load_dotenv()
    
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
    
    # Test texts
    test_texts = [
        "Spanish localization on Team Page",
        "Live game MIG validations",
        "Jewel event regressions"
    ]
    
    # Test with configured provider
    provider = os.getenv("EMBED_PROVIDER", "openai")
    logger.info(f"Testing {provider} embedder")
    
    try:
        embedder = get_embedder()
        
        # Test single text
        single_embedding = embedder.embed(test_texts[0])
        logger.info(f"Single embedding shape: {len(single_embedding)}")
        
        # Test batch
        batch_embeddings = embedder.embed(test_texts)
        logger.info(f"Batch embeddings shape: {len(batch_embeddings)}x{len(batch_embeddings[0])}")
        
        # Show stats
        logger.info("Embedding stats", stats=embedder.get_stats())
        
    except Exception as e:
        logger.error(f"Embedding test failed: {e}")