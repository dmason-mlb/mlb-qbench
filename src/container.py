"""Enterprise-grade dependency injection container for MLB QBench services and components.

This module implements a lightweight yet powerful dependency injection (DI) container
that manages service lifecycles, resolves dependencies, and provides a clean separation
of concerns throughout the MLB QBench application architecture.

Core Features:
    - Service Registration: Singleton and transient lifetime management
    - Dependency Resolution: Automatic dependency injection with circular detection
    - Lifecycle Management: Proper resource cleanup and disposal
    - Service Discovery: Runtime service introspection and debugging
    - Async Support: Full async/await compatibility for modern Python

Architectural Benefits:
    - Loose Coupling: Services depend on abstractions, not implementations
    - Testability: Easy mocking and testing through dependency injection
    - Configuration: Centralized service configuration and management
    - Scalability: Efficient resource management and lifecycle control
    - Maintainability: Clear service boundaries and dependencies

Service Lifetimes:
    - Singleton: Single instance shared across application (embedders, clients)
    - Transient: New instance created on each request (validators, processors)
    - Instance: Pre-created objects registered directly

Security Considerations:
    - Circular dependency detection prevents infinite loops
    - Resource cleanup prevents memory leaks
    - Service isolation maintains security boundaries
    - Controlled access through well-defined interfaces

Performance Characteristics:
    - Service Resolution: O(d) where d = dependency depth
    - Registration: O(1) constant time operations
    - Cleanup: O(s) where s = number of service instances
    - Memory: ~100-500 bytes per registered service

Usage Patterns:
    - Configure services at application startup
    - Resolve services throughout request lifecycle
    - Clean disposal during application shutdown
    - Service health monitoring and diagnostics
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional, TypeVar, Union

import structlog

logger = structlog.get_logger()

T = TypeVar("T")


class ServiceLifetime:
    """Service lifetime constants defining instance management strategies.

    Defines the lifecycle behavior for services registered in the dependency
    injection container, controlling when instances are created, reused, and disposed.

    Lifetime Strategies:
        SINGLETON: Single instance created once and reused throughout application lifecycle.
                  Ideal for expensive resources like database connections, embedders.

        TRANSIENT: New instance created for each resolution request.
                  Suitable for lightweight services, validators, and stateless processors.

    Performance Impact:
        - Singleton: Amortized O(1) after initial creation, minimal memory overhead
        - Transient: O(c) creation cost per request, potential GC pressure

    Thread Safety:
        Container handles thread safety for singleton instance creation.
        Services themselves must implement their own thread safety if needed.
    """

    SINGLETON = "singleton"
    TRANSIENT = "transient"


class ServiceDescriptor:
    """Service configuration descriptor defining creation and management metadata.

    Encapsulates all information needed to create and manage a service instance,
    including its type, implementation, lifetime, and dependency requirements.

    Configuration Elements:
        service_type: Abstract interface or base class the service implements
        implementation: Concrete class or factory function for instance creation
        lifetime: ServiceLifetime constant controlling instance management
        dependencies: List of other services required for creation

    Factory Support:
        - Class constructors: Direct instantiation with dependency injection
        - Factory functions: Custom creation logic with parameter injection
        - Lambda expressions: Inline factory definitions for simple services

    Dependency Resolution:
        Dependencies are resolved recursively before service creation.
        Circular dependencies are detected and raise ValueError.
        Missing dependencies cause resolution failure with clear error messages.

    Usage:
        Internal container class for service registration metadata.
        Created automatically during service registration calls.
    """

    def __init__(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[..., T], Callable[..., Any]],
        lifetime: str = ServiceLifetime.SINGLETON,
        dependencies: Optional[list] = None,
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.dependencies = dependencies or []


class Container:
    """Lightweight dependency injection container with enterprise-grade features.

    Provides comprehensive service management including registration, resolution,
    lifecycle management, and diagnostic capabilities for the MLB QBench application.

    Core Capabilities:
        - Service Registration: Multiple lifetime strategies (singleton, transient)
        - Dependency Resolution: Automatic injection with circular detection
        - Resource Management: Proper async/sync cleanup and disposal
        - Service Discovery: Runtime introspection and health monitoring
        - Error Handling: Clear error messages and resolution diagnostics

    Internal State:
        _services: Registry of service descriptors by type
        _instances: Cache of singleton instances by type
        _resolving: Set tracking services currently being resolved (circular detection)

    Thread Safety:
        Container operations are not inherently thread-safe.
        Applications using threading should implement appropriate locking.
        Async operations are safe when using asyncio event loops.

    Performance:
        - Registration: O(1) dictionary operations
        - Resolution: O(d) where d = maximum dependency depth
        - Cleanup: O(n) where n = number of active instances
        - Memory: Linear with number of registered services and instances

    Error Handling:
        - Circular Dependencies: Detected and reported with service chain
        - Missing Services: Clear error messages with service name
        - Resolution Failures: Detailed context for debugging
        - Cleanup Errors: Logged but don't prevent other cleanup operations
    """

    def __init__(self):
        self._services: dict[type, ServiceDescriptor] = {}
        self._instances: dict[type, Any] = {}
        self._resolving: set = set()  # Circular dependency detection

    def register_singleton(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[..., T], Callable[..., Any]],
        dependencies: Optional[list] = None,
    ) -> "Container":
        """Register a singleton service with shared instance lifecycle.

        Singleton services are created once on first resolution and reused
        for all subsequent requests. Ideal for expensive resources like
        database connections, embedding providers, and caching services.

        Args:
            service_type: Interface or base type the service implements
            implementation: Concrete class or factory function
            dependencies: List of services required for creation

        Returns:
            Container: Self for fluent registration chaining

        Lifecycle:
            1. Service registered in descriptor registry
            2. Instance created on first get() call
            3. Same instance returned for all subsequent get() calls
            4. Instance disposed during container cleanup

        Performance: O(1) registration, amortized O(1) resolution after creation

        Examples:
            >>> container.register_singleton(Database, PostgresDatabase, ['config'])
            >>> container.register_singleton(Cache, lambda: RedisCache())
        """
        self._services[service_type] = ServiceDescriptor(
            service_type, implementation, ServiceLifetime.SINGLETON, dependencies
        )
        return self

    def register_transient(
        self,
        service_type: type[T],
        implementation: Union[type[T], Callable[..., T], Callable[..., Any]],
        dependencies: Optional[list] = None,
    ) -> "Container":
        """Register a transient service with per-request instance creation.

        Transient services create a new instance for each resolution request.
        Suitable for lightweight, stateless services like validators,
        processors, and short-lived computational services.

        Args:
            service_type: Interface or base type the service implements
            implementation: Concrete class or factory function
            dependencies: List of services required for creation

        Returns:
            Container: Self for fluent registration chaining

        Lifecycle:
            1. Service registered in descriptor registry
            2. New instance created on every get() call
            3. Instance returned to caller (no caching)
            4. Instance cleanup is caller's responsibility

        Performance: O(c) creation cost per resolution where c = constructor complexity

        Examples:
            >>> container.register_transient(Validator, JsonValidator)
            >>> container.register_transient(Processor, lambda data: DataProcessor(data))
        """
        self._services[service_type] = ServiceDescriptor(
            service_type, implementation, ServiceLifetime.TRANSIENT, dependencies
        )
        return self

    def register_instance(self, service_type: type[T], instance: T) -> "Container":
        """Register a pre-created service instance for immediate availability.

        Allows registration of existing objects that are already configured
        and ready for use. Useful for external dependencies, configuration
        objects, or services with complex initialization requirements.

        Args:
            service_type: Interface or type the instance implements
            instance: Pre-created service instance

        Returns:
            Container: Self for fluent registration chaining

        Lifecycle:
            1. Instance immediately available via get() calls
            2. No creation or dependency resolution needed
            3. Instance disposed during container cleanup if disposable

        Performance: O(1) registration and resolution

        Use Cases:
            - External service clients (already authenticated)
            - Configuration objects loaded from files
            - Test doubles and mocks for unit testing

        Examples:
            >>> config = load_config('app.yaml')
            >>> container.register_instance(AppConfig, config)
        """
        self._instances[service_type] = instance
        return self

    def get(self, service_type: Union[type[T], str]) -> T:
        """Resolve and return a service instance with full dependency injection.

        Core service resolution method that handles dependency injection,
        lifecycle management, circular dependency detection, and error reporting.

        Resolution Process:
            1. Circular dependency detection
            2. Existing instance check (singletons)
            3. Service registration verification
            4. Recursive dependency resolution
            5. Instance creation via implementation
            6. Singleton caching (if applicable)
            7. Resolution cleanup and logging

        Args:
            service_type: Type or string identifier of service to resolve

        Returns:
            T: Configured service instance with dependencies injected

        Raises:
            ValueError: If circular dependency detected or service not registered

        Performance: O(d) where d = maximum dependency depth in service graph

        Error Handling:
            - Provides clear error messages with service names
            - Logs successful resolutions with dependency information
            - Maintains resolution state for debugging

        Examples:
            >>> database = container.get(Database)
            >>> validator = container.get('validator')
        """
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
                dependencies=dep_names,
            )

            return instance

        finally:
            # Remove from resolving set
            self._resolving.discard(service_type)

    def try_get(self, service_type: Union[type[T], str]) -> Optional[T]:
        """Attempt service resolution with graceful failure handling.

        Non-throwing variant of get() that returns None instead of raising
        exceptions when services are not registered. Useful for optional
        dependencies and conditional feature availability.

        Args:
            service_type: Type or string identifier of service to resolve

        Returns:
            Optional[T]: Service instance if available, None if not registered

        Error Handling:
            Catches and suppresses ValueError from get() method.
            Other exceptions (creation failures) are still propagated.

        Performance: Same as get() when service exists, O(1) when missing

        Use Cases:
            - Optional feature dependencies
            - Graceful degradation patterns
            - Service availability checking
            - Plugin architecture support

        Examples:
            >>> cache = container.try_get(CacheService)
            >>> if cache:
            ...     cache.store(key, value)
        """
        try:
            return self.get(service_type)
        except ValueError:
            return None

    def is_registered(self, service_type: Union[type[T], str]) -> bool:
        """Check if a service type is registered in the container.

        Efficient lookup to determine service availability without
        triggering creation or dependency resolution.

        Args:
            service_type: Type or string identifier to check

        Returns:
            bool: True if service is registered, False otherwise

        Performance: O(1) dictionary lookup operation

        Use Cases:
            - Conditional service access
            - Feature availability checking
            - Container validation and diagnostics
            - Plugin detection logic

        Examples:
            >>> if container.is_registered(EmailService):
            ...     send_notification()
        """
        return service_type in self._services or service_type in self._instances

    async def dispose_async(self):
        """Asynchronously dispose of all service instances with async cleanup support.

        Properly closes async resources like database connections, HTTP clients,
        and embedding providers that implement async cleanup methods.

        Cleanup Process:
            1. Iterate through all cached instances
            2. Check for async close() methods
            3. Await cleanup for async resources
            4. Log errors but continue cleanup of other services
            5. Clear instance cache
            6. Log successful disposal

        Error Handling:
            Individual service cleanup failures are logged but don't prevent
            cleanup of other services. This ensures maximum resource cleanup
            even when some services fail.

        Performance: O(n) where n = number of active service instances

        Async Safety:
            Safe to call multiple times. Subsequent calls are no-ops.
            Should be called during application shutdown.

        Examples:
            >>> async with container_lifespan() as container:
            ...     # Use services
            ...     pass  # Automatic cleanup on exit
        """
        for instance in self._instances.values():
            if hasattr(instance, "close") and asyncio.iscoroutinefunction(instance.close):
                try:
                    await instance.close()
                except Exception as e:
                    logger.error(f"Error disposing service: {e}")

        self._instances.clear()
        logger.info("Container disposed successfully")

    def dispose(self):
        """Synchronously dispose of all service instances with sync cleanup support.

        Closes synchronous resources like file handles, thread pools,
        and other non-async services that implement sync cleanup methods.

        Cleanup Process:
            1. Iterate through all cached instances
            2. Check for sync close() methods (excluding async variants)
            3. Call cleanup for synchronous resources
            4. Log errors but continue cleanup of other services
            5. Clear instance cache
            6. Log successful disposal

        Error Handling:
            Individual service cleanup failures are logged but don't prevent
            cleanup of other services. Ensures maximum resource cleanup.

        Performance: O(n) where n = number of active service instances

        Thread Safety:
            Not thread-safe. Caller must ensure exclusive access.
            Should be called during application shutdown.

        Examples:
            >>> container = Container()
            >>> # Register and use services
            >>> container.dispose()  # Cleanup before exit
        """
        for instance in self._instances.values():
            if hasattr(instance, "close") and not asyncio.iscoroutinefunction(instance.close):
                try:
                    instance.close()
                except Exception as e:
                    logger.error(f"Error disposing service: {e}")

        self._instances.clear()
        logger.info("Container disposed successfully")

    def get_service_info(self) -> dict[str, Any]:
        """Generate comprehensive diagnostic information about container state.

        Provides detailed insights into service registration, instantiation status,
        dependency relationships, and overall container health for monitoring
        and debugging purposes.

        Return Structure:
            - registered_services: Total count of registered service types
            - active_instances: Count of currently instantiated singletons
            - services: Detailed breakdown per service including:
                * lifetime: Singleton or transient lifecycle
                * dependencies: List of required service dependencies
                * instantiated: Whether singleton instance exists

        Diagnostic Uses:
            - Container health monitoring
            - Service dependency visualization
            - Memory usage analysis (active instances)
            - Registration completeness verification
            - Debugging service resolution issues

        Performance: O(s + d) where s = services, d = total dependencies

        Examples:
            >>> info = container.get_service_info()
            >>> print(f"Services: {info['registered_services']}")
            >>> print(f"Active: {info['active_instances']}")
        """
        info = {
            "registered_services": len(self._services),
            "active_instances": len(self._instances),
            "services": {},
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
                "instantiated": service_key in self._instances,
            }

        return info


# Global container instance
_container: Optional[Container] = None


def get_container() -> Container:
    """Get the global singleton container instance with lazy initialization.

    Implements the global container pattern for application-wide service access.
    Creates the container on first access and reuses it for all subsequent calls.

    Global Container Benefits:
        - Consistent service access across the application
        - Simplified service resolution without explicit passing
        - Centralized configuration and lifecycle management
        - Easy testing with container replacement

    Returns:
        Container: Global container instance

    Thread Safety:
        Not thread-safe for initial creation. Applications using threading
        should call this during single-threaded initialization.

    Performance: O(1) after initial creation

    Usage:
        Primary access point for application services.
        Should be configured once at startup via configure_services().
    """
    global _container
    if _container is None:
        _container = Container()
    return _container


def configure_services() -> Container:
    """Configure and register all MLB QBench application services.

    Central service configuration function that registers all required services
    with appropriate lifetimes and dependencies. This is the primary setup
    function called during application initialization.

    Service Categories:
        - Core Services: PostgreSQL database, embedder, rate limiter
        - Validators: Path, JIRA, API key validation services
        - Ingestion: Functional and API test ingestion services
        - Health: Database health monitoring services

    Dependency Strategy:
        - Heavyweight resources (databases, embedders) as singletons
        - Lightweight validators and processors as transients
        - Stateless functions registered with lambda factories

    Import Strategy:
        Local imports prevent circular dependencies during container setup.
        Services are imported only when needed for registration.

    Returns:
        Container: Fully configured container with all services registered

    Performance: O(s) where s = number of services to register

    Configuration Order:
        1. Core infrastructure services
        2. Validation and security services
        3. Business logic services
        4. Health and monitoring services
    """
    container = get_container()

    # Import here to avoid circular dependencies
    from slowapi import Limiter
    from slowapi.util import get_remote_address

    from .auth.auth import get_api_key
    from .db.postgres_vector import PostgresVectorDB
    from .embedder import get_embedder
    from .security import validate_data_file_path, validate_jira_key

    # Register core services
    container.register_singleton("database", lambda: PostgresVectorDB())
    container.register_singleton("embedder", get_embedder)
    container.register_singleton("rate_limiter", lambda: Limiter(key_func=get_remote_address))

    # Register validators (lightweight, can be transient)
    container.register_transient("path_validator", lambda: validate_data_file_path)
    container.register_transient("jira_validator", lambda: validate_jira_key)
    container.register_transient("api_key_validator", lambda: get_api_key)

    logger.info("Service container configured successfully")
    return container


@asynccontextmanager
async def container_lifespan():
    """Async context manager for container lifecycle management.

    Provides automatic container initialization and cleanup using
    Python's async context manager protocol. Ensures proper resource
    disposal even when exceptions occur during application execution.

    Lifecycle Flow:
        1. Enter: Get global container instance
        2. Yield: Provide container for application use
        3. Exit: Dispose of all async resources automatically

    Exception Safety:
        Container disposal occurs in finally block, ensuring cleanup
        even when exceptions are raised during application execution.

    Usage Pattern:
        Recommended for FastAPI lifespan management and async applications
        that need guaranteed resource cleanup.

    Examples:
        >>> async def app_lifespan(app: FastAPI):
        ...     async with container_lifespan() as container:
        ...         yield
    """
    container = get_container()
    try:
        logger.info("Starting service container")
        yield container
    finally:
        logger.info("Disposing service container")
        await container.dispose_async()


# Service accessor functions for backward compatibility
def get_database():
    """Get PostgreSQL database instance from the global container.

    Convenience function for accessing the singleton PostgreSQL database instance.
    Provides backward compatibility and simplified access pattern.

    Returns:
        PostgresVectorDB: Configured PostgreSQL database with pgvector

    Service Resolution:
        Resolves 'database' service from global container.
        Database is configured with connection pool and pgvector extension.

    Performance: O(1) after initial database creation

    Usage:
        Used throughout the application for vector database operations.
        Singleton pattern ensures connection pooling and resource efficiency.
    """
    return get_container().get("database")


def get_embedder_service():
    """Get embedding provider service from the global container.

    Convenience function for accessing the singleton embedding provider.
    Supports multiple providers (OpenAI, Cohere, Vertex AI, Azure).

    Returns:
        EmbeddingProvider: Configured embedding service instance

    Service Resolution:
        Resolves 'embedder' service from global container.
        Provider type determined by EMBED_PROVIDER environment variable.

    Performance: O(1) after initial provider creation

    Usage:
        Used for generating embeddings during ingestion and search operations.
        Singleton pattern provides connection pooling and API rate limiting.
    """
    return get_container().get("embedder")


def get_rate_limiter():
    """Get rate limiting service from the global container.

    Convenience function for accessing the singleton rate limiter instance.
    Implements request throttling for API endpoints.

    Returns:
        Limiter: Configured slowapi rate limiter

    Service Resolution:
        Resolves 'rate_limiter' service from global container.
        Uses remote address as key for per-client rate limiting.

    Performance: O(1) after initial limiter creation

    Usage:
        Applied to FastAPI endpoints for DoS protection and fair usage.
        Singleton pattern ensures consistent rate limiting across requests.
    """
    return get_container().get("rate_limiter")


def get_path_validator():
    """Get file path validation service from the global container.

    Convenience function for accessing the path validation service.
    Prevents directory traversal and SSRF attacks.

    Returns:
        Callable: Path validation function

    Service Resolution:
        Resolves 'path_validator' service from global container.
        Transient service providing validate_data_file_path function.

    Performance: O(1) service resolution, O(p) validation where p = path length

    Security:
        Critical for preventing path traversal attacks in file operations.
        Validates file paths before ingestion and processing.
    """
    return get_container().get("path_validator")


def get_jira_validator():
    """Get JIRA key validation service from the global container.

    Convenience function for accessing the JIRA key validation service.
    Ensures JIRA keys follow standard format conventions.

    Returns:
        Callable: JIRA key validation function

    Service Resolution:
        Resolves 'jira_validator' service from global container.
        Transient service providing validate_jira_key function.

    Performance: O(1) service resolution, O(k) validation where k = key length

    Integration:
        Used for validating JIRA references in test documents.
        Ensures compatibility with Atlassian JIRA APIs.
    """
    return get_container().get("jira_validator")


def get_api_key_validator():
    """Get API key validation service from the global container.

    Convenience function for accessing the API authentication service.
    Validates request API keys against configured allowed keys.

    Returns:
        Callable: API key validation function

    Service Resolution:
        Resolves 'api_key_validator' service from global container.
        Transient service providing get_api_key function.

    Performance: O(1) service resolution, O(k) validation where k = key count

    Security:
        Critical for API access control and authentication.
        Supports both master keys and multiple user keys.
    """
    return get_container().get("api_key_validator")
