"""Dependency injection container for MLB QBench services."""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional, TypeVar, Union

import structlog

logger = structlog.get_logger()

T = TypeVar('T')


class ServiceLifetime:
    """Service lifetime management."""
    SINGLETON = "singleton"
    TRANSIENT = "transient"


class ServiceDescriptor:
    """Describes how a service should be created and managed."""

    def __init__(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[..., T], Callable[..., Any]],
        lifetime: str = ServiceLifetime.SINGLETON,
        dependencies: Optional[list] = None
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.dependencies = dependencies or []


class Container:
    """Simple dependency injection container."""

    def __init__(self):
        self._services: dict[type, ServiceDescriptor] = {}
        self._instances: dict[type, Any] = {}
        self._resolving: set = set()  # Circular dependency detection

    def register_singleton(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[..., T], Callable[..., Any]],
        dependencies: Optional[list] = None
    ) -> 'Container':
        """Register a singleton service."""
        self._services[service_type] = ServiceDescriptor(
            service_type, implementation, ServiceLifetime.SINGLETON, dependencies
        )
        return self

    def register_transient(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[..., T], Callable[..., Any]],
        dependencies: Optional[list] = None
    ) -> 'Container':
        """Register a transient service."""
        self._services[service_type] = ServiceDescriptor(
            service_type, implementation, ServiceLifetime.TRANSIENT, dependencies
        )
        return self

    def register_instance(self, service_type: type[T], instance: T) -> 'Container':
        """Register a pre-created instance."""
        self._instances[service_type] = instance
        return self

    def get(self, service_type: Union[type[T], str]) -> T:
        """Get a service instance."""
        # Get service name for error messages
        service_name = service_type if isinstance(service_type, str) else service_type.__name__
        
        # Check for circular dependencies
        if service_type in self._resolving:
            raise ValueError(f"Circular dependency detected for {service_name}")

        # Return existing instance if it's a singleton
        if service_type in self._instances:
            return self._instances[service_type]

        # Check if service is registered
        if service_type not in self._services:
            raise ValueError(f"Service {service_name} is not registered")

        descriptor = self._services[service_type]

        # Mark as resolving for circular dependency detection
        self._resolving.add(service_type)

        try:
            # Resolve dependencies
            resolved_dependencies = []
            for dep_type in descriptor.dependencies:
                resolved_dependencies.append(self.get(dep_type))

            # Create instance
            if callable(descriptor.implementation):
                instance = descriptor.implementation(*resolved_dependencies)
            else:
                instance = descriptor.implementation(*resolved_dependencies)

            # Store singleton instances
            if descriptor.lifetime == ServiceLifetime.SINGLETON:
                self._instances[service_type] = instance

            # Get dependency names for logging
            dep_names = []
            for dep in descriptor.dependencies:
                if isinstance(dep, str):
                    dep_names.append(dep)
                else:
                    dep_names.append(dep.__name__)

            logger.debug(
                "Service resolved successfully",
                service=service_name,
                lifetime=descriptor.lifetime,
                dependencies=dep_names
            )

            return instance

        finally:
            # Remove from resolving set
            self._resolving.discard(service_type)

    def try_get(self, service_type: Union[type[T], str]) -> Optional[T]:
        """Try to get a service instance, return None if not registered."""
        try:
            return self.get(service_type)
        except ValueError:
            return None

    def is_registered(self, service_type: Union[type[T], str]) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services or service_type in self._instances

    async def dispose_async(self):
        """Dispose of async resources."""
        for instance in self._instances.values():
            if hasattr(instance, 'close') and asyncio.iscoroutinefunction(instance.close):
                try:
                    await instance.close()
                except Exception as e:
                    logger.error(f"Error disposing service: {e}")

        self._instances.clear()
        logger.info("Container disposed successfully")

    def dispose(self):
        """Dispose of synchronous resources."""
        for instance in self._instances.values():
            if hasattr(instance, 'close') and not asyncio.iscoroutinefunction(instance.close):
                try:
                    instance.close()
                except Exception as e:
                    logger.error(f"Error disposing service: {e}")

        self._instances.clear()
        logger.info("Container disposed successfully")

    def get_service_info(self) -> dict[str, Any]:
        """Get information about registered services."""
        info = {
            "registered_services": len(self._services),
            "active_instances": len(self._instances),
            "services": {}
        }

        for service_key, descriptor in self._services.items():
            # Handle both string keys and type keys
            service_name = service_key if isinstance(service_key, str) else service_key.__name__
            dependency_names = []
            for dep in descriptor.dependencies:
                if isinstance(dep, str):
                    dependency_names.append(dep)
                else:
                    dependency_names.append(dep.__name__)

            info["services"][service_name] = {
                "lifetime": descriptor.lifetime,
                "dependencies": dependency_names,
                "instantiated": service_key in self._instances
            }

        return info


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global container instance."""
    global _container
    if _container is None:
        _container = Container()
    return _container


def configure_services() -> Container:
    """Configure all application services."""
    container = get_container()

    # Import here to avoid circular dependencies
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    from .auth.auth import get_api_key
    from .embedder import get_embedder
    from .ingest.ingest_api import ingest_api_tests
    from .ingest.ingest_functional import ingest_functional_tests
    from .models.schema import check_collections_health, get_client
    from .security import validate_data_file_path, validate_jira_key

    # Register core services
    container.register_singleton('qdrant_client', get_client)
    container.register_singleton('embedder', get_embedder)
    container.register_singleton('rate_limiter', lambda: Limiter(key_func=get_remote_address))

    # Register validators (lightweight, can be transient)
    container.register_transient('path_validator', lambda: validate_data_file_path)
    container.register_transient('jira_validator', lambda: validate_jira_key)
    container.register_transient('api_key_validator', lambda: get_api_key)

    # Register ingestion services (stateless, can be transient)
    container.register_transient('functional_ingest', lambda: ingest_functional_tests)
    container.register_transient('api_ingest', lambda: ingest_api_tests)

    # Register health check service
    container.register_transient('health_checker', lambda client: lambda: check_collections_health(client), ['qdrant_client'])

    logger.info("Service container configured successfully")
    return container


@asynccontextmanager
async def container_lifespan():
    """Manage container lifecycle."""
    container = get_container()
    try:
        logger.info("Starting service container")
        yield container
    finally:
        logger.info("Disposing service container")
        await container.dispose_async()


# Service accessor functions for backward compatibility
def get_qdrant_client():
    """Get Qdrant client from container."""
    return get_container().get('qdrant_client')


def get_embedder_service():
    """Get embedder from container."""
    return get_container().get('embedder')


def get_rate_limiter():
    """Get rate limiter from container."""
    return get_container().get('rate_limiter')


def get_path_validator():
    """Get path validator from container."""
    return get_container().get('path_validator')


def get_jira_validator():
    """Get JIRA validator from container."""
    return get_container().get('jira_validator')


def get_api_key_validator():
    """Get API key validator from container."""
    return get_container().get('api_key_validator')


def get_health_checker():
    """Get health checker from container."""
    return get_container().get('health_checker')
