.PHONY: help dev stop clean test ingest search lint format install
.PHONY: postgres-setup postgres-schema migrate-test migrate-full postgres-clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python dependencies
	pip install -e .
	pip install -e ".[dev]"

# PostgreSQL targets
postgres-setup: ## Set up PostgreSQL with pgvector extension
	@echo "Setting up PostgreSQL with pgvector..."
	./scripts/setup_postgres.sh

postgres-schema: ## Create PostgreSQL schema and indexes
	@echo "Creating PostgreSQL schema..."
	psql -U postgres -d mlb_qbench -f sql/create_schema.sql

migrate-test: ## Test migration with 1000 records
	@echo "Running test migration (1000 records)..."
	python scripts/migrate_from_sqlite.py --limit 1000

migrate-full: ## Run full migration of all test cases
	@echo "Running full migration (104k+ records)..."
	@echo "This will take some time and use OpenAI API quota..."
	python scripts/migrate_from_sqlite.py

postgres-clean: ## Drop and recreate PostgreSQL database
	@echo "Dropping and recreating database..."
	dropdb -U postgres mlb_qbench --if-exists
	createdb -U postgres mlb_qbench
	psql -U postgres -d mlb_qbench -c "CREATE EXTENSION vector;"
	make postgres-schema

# API development
dev: ## Start API server with PostgreSQL
	@echo "Starting API server with PostgreSQL..."
	@echo "Note: Set DATABASE_URL, EMBED_PROVIDER, and API keys in .env"
	uvicorn src.service.main:app --reload --host 0.0.0.0 --port 8000

stop: ## Stop all services
	docker-compose down
	@pkill -f "uvicorn main:app" || true

clean: stop ## Stop services and clean data
	rm -rf qdrant_storage
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

test: ## Run all tests
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term

ingest: ## Ingest sample test data
	@echo "Ingesting functional tests..."
	python -m src.ingest.ingest_functional data/functional_tests_normalized.json
	@echo "Ingesting API tests..."
	python -m src.ingest.ingest_api data/api_tests_normalized.json

search: ## Run example search queries
	@echo "Testing search queries..."
	python -m scripts.test_search

lint: ## Run linting and type checks
	ruff check src/ tests/
	mypy src/

format: ## Format code with black
	black src/ tests/
	ruff check --fix src/ tests/

qdrant-up: ## Start only Qdrant
	docker-compose up -d qdrant

qdrant-down: ## Stop only Qdrant
	docker-compose stop qdrant

api-dev: ## Start only API server (assumes Qdrant is running)
	uvicorn src.service.main:app --reload --host 0.0.0.0 --port 8000

check-env: ## Verify environment variables
	@python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('EMBED_PROVIDER:', os.getenv('EMBED_PROVIDER', 'NOT SET'))"
	@python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('QDRANT_URL:', os.getenv('QDRANT_URL', 'NOT SET'))"

mcp-server: ## Run MCP server for AI integration
	@echo "Starting MCP server..."
	API_BASE_URL=$${API_BASE_URL:-http://localhost:8000} python -m src.mcp