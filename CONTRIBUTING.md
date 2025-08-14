# Contributing to MLB QBench

Thank you for your interest in contributing to MLB QBench! This guide will help you get started with contributing to our test retrieval service.

## Welcome & Scope

We welcome contributions in the following areas:
- 🐛 Bug fixes and issue reports
- ✨ New features and enhancements
- 📚 Documentation improvements
- 🧪 Test coverage expansion
- 🎨 Code quality improvements
- 🔌 New embedding provider integrations

## Quick Start for Contributors

The fastest path to start contributing:

```bash
# Clone and setup
git clone <your-fork-url>
cd mlb-qbench

# Install with dev dependencies
pip install -e ".[dev]"

# Copy environment configuration
cp .env.example .env
# Edit .env with your API keys

# Start services and run tests
make dev         # Starts Qdrant + API server
make test        # In another terminal
```

For detailed environment setup, see the [README.md](README.md).

## Toolchain & Prerequisites

### Required Software

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.9+ | Core runtime |
| Docker | Latest | Qdrant database |
| Docker Compose | Latest | Service orchestration |
| pip | Latest | Package management |

### Embedding Provider Requirements

You'll need at least one embedding provider API key:
- **OpenAI**: `OPENAI_API_KEY`
- **Cohere**: `COHERE_API_KEY`
- **Google Vertex AI**: `VERTEX_PROJECT_ID` + credentials
- **Azure OpenAI**: `AZURE_OPENAI_API_KEY` + endpoint

## Project Setup & Local Development

### 1. Environment Configuration

```bash
# Copy example environment
cp .env.example .env

# Required variables (edit .env):
QDRANT_URL=http://localhost:6533
EMBED_PROVIDER=openai  # or cohere, vertex, azure
EMBED_MODEL=text-embedding-3-large
OPENAI_API_KEY=your-key  # Or appropriate provider key
```

### 2. Install Dependencies

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import mlb_qbench; print('✓ Installation successful')"
```

### 3. Start Services

```bash
# Start Qdrant database
make qdrant-up

# Start API server (separate terminal)
make api-dev

# Or start both together
make dev
```

### 4. Verify Setup

```bash
# Check environment
make check-env

# Run health check
curl http://localhost:8000/healthz
```

## Quality Gates

All contributions must pass the following quality checks:

### Linting & Formatting

| Command | Purpose | Configuration |
|---------|---------|---------------|
| `make lint` | Run ruff + mypy checks | `pyproject.toml` |
| `make format` | Auto-format with black + ruff | `pyproject.toml` |
| `ruff check src/ tests/` | Linting only | `[tool.ruff]` section |
| `mypy src/` | Type checking | `[tool.mypy]` section |
| `black src/ tests/` | Code formatting | `[tool.black]` section |

### Testing

| Command | Purpose | Coverage |
|---------|---------|----------|
| `make test` | Full test suite with coverage | HTML + terminal report |
| `pytest tests/ -v` | Verbose test output | - |
| `pytest tests/test_auth.py` | Single test file | - |
| `pytest -k "test_name"` | Specific test | - |

**Coverage Requirements**: New code should maintain or improve the current coverage level.

## Branching & Commits

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`
- Refactor: `refactor/description`

### Commit Style

While not enforced, we recommend conventional commits:

```
type(scope): description

feat(embedder): add support for new provider
fix(search): handle empty query gracefully
docs(api): update endpoint documentation
test(auth): add coverage for edge cases
```

## Project Structure

```
mlb-qbench/
├── src/
│   ├── auth/           # API authentication
│   ├── ingest/         # Data ingestion modules
│   ├── mcp/            # MCP server integration
│   ├── models/         # Pydantic models
│   ├── security/       # Security utilities
│   ├── service/        # FastAPI application
│   ├── container.py    # Dependency injection
│   └── embedder.py     # Embedding providers
├── tests/              # Test suite
├── scripts/            # Utility scripts
└── docs/               # Documentation
```

## Common Development Tasks

### Adding a New Embedding Provider

1. Create a new class in `src/embedder.py`:
```python
class NewProvider(EmbeddingProvider):
    async def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        # Implementation
```

2. Add to the factory in `get_embedder()`:
```python
if provider == "newprovider":
    return NewProvider(...)
```

3. Update `.env.example` with required variables
4. Add tests in `tests/test_embedder.py`

### Modifying the Test Schema

1. Update models in `src/models/test_models.py`
2. Update normalization in `src/ingest/normalize.py`
3. Update collection schema in `src/models/schema.py` if adding indexes
4. Update ingestion modules in `src/ingest/`
5. Add migration script if needed for existing data

### Running the Test Matrix

```bash
# Run specific test categories
pytest tests/test_auth.py -v          # Authentication tests
pytest tests/test_health_endpoint.py  # Health checks
pytest tests/test_ingestion_security.py  # Security tests

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Run async tests
pytest tests/ -v --asyncio-mode=auto
```

## Pull Request Process

### Before Submitting

1. **Run quality checks**:
   ```bash
   make lint
   make format
   make test
   ```

2. **Update documentation** if you've changed APIs or added features

3. **Write/update tests** for your changes

4. **Test locally** with real data if possible

### PR Guidelines

- **Title**: Clear, descriptive summary
- **Description**: What, why, and how
- **Size**: Keep PRs focused and atomic
- **Tests**: Include tests for new functionality
- **Documentation**: Update relevant docs
- **Breaking changes**: Clearly marked if any

### Review Process

1. All PRs require at least one review
2. Address review feedback promptly
3. Keep discussions focused and professional
4. Squash commits before merging if requested

## Issue Reports

When reporting issues, please include:

1. **Environment**:
   - Python version: `python --version`
   - OS: `uname -a` or Windows version
   - Docker version: `docker --version`

2. **Configuration**:
   - Embedding provider used
   - Relevant `.env` settings (without secrets)

3. **Steps to reproduce**:
   - Minimal code/commands
   - Expected vs actual behavior

4. **Logs/Errors**:
   - Full error messages
   - Relevant log output

## API Development

### Adding New Endpoints

1. Define endpoint in `src/service/main.py`
2. Add Pydantic models for request/response
3. Implement business logic with async patterns
4. Add rate limiting if needed
5. Write tests in `tests/`
6. Update API documentation

### Security Considerations

- Never log sensitive data (API keys, tokens)
- Validate all inputs with Pydantic
- Use parameterized queries for Qdrant
- Implement rate limiting for expensive operations
- Follow security best practices in `src/security/`

## Performance Guidelines

### Async Best Practices

- Use `async/await` consistently
- Batch operations when possible (see `embedder.py`)
- Use `asyncio.gather()` for concurrent operations
- Properly handle async context managers

### Resource Management

- Default batch sizes: 25 texts for embeddings, 50 for ingestion
- Qdrant timeout: 30 seconds
- Embedding timeout: 60 seconds
- Connection pooling for HTTP clients

## Documentation

### Code Documentation

- Use type hints for all functions
- Write docstrings for public APIs
- Include usage examples for complex functions
- Keep `CLAUDE.md` updated for AI assistance

### User Documentation

- Update README.md for user-facing changes
- Document new environment variables in `.env.example`
- Add configuration examples
- Include troubleshooting tips

## Security Reporting

For security vulnerabilities:

1. **DO NOT** open a public issue
2. Contact the maintainers directly (see LICENSE.md for contact)
3. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix if available

## Style Guides

### Python Style

- Follow PEP 8 with exceptions defined in `pyproject.toml`
- Line length: 100 characters
- Use type hints throughout
- Async functions should be prefixed with `async def`

### Import Order (enforced by ruff)

1. Standard library imports
2. Third-party imports
3. Local application imports

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors appropriately with structlog
- Handle async exceptions properly

## Makefile Targets Reference

| Command | Description |
|---------|-------------|
| `make help` | Show all available targets |
| `make install` | Install dependencies |
| `make dev` | Start Qdrant + API server |
| `make stop` | Stop all services |
| `make clean` | Clean all data and caches |
| `make test` | Run test suite with coverage |
| `make lint` | Run linting checks |
| `make format` | Auto-format code |
| `make qdrant-up` | Start Qdrant only |
| `make qdrant-down` | Stop Qdrant only |
| `make api-dev` | Start API server only |
| `make check-env` | Verify environment setup |
| `make ingest` | Ingest sample data |
| `make mcp-server` | Start MCP server |

## License & Attribution

By contributing, you agree that your contributions will be licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

## Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Review the [README.md](README.md) and [CLAUDE.md](CLAUDE.md)
3. Open a discussion for general questions
4. Contact maintainers for sensitive topics

Thank you for contributing to MLB QBench! 🚀