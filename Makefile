# Unified Command Toolkit for events-with-fast-api project

.PHONY: help dev debug logs shell db status stop clean build test test-unit test-integration test-coverage test-watch test-db-setup test-db-cleanup install-dev lint format makemigrations migrate test-quick test-file typecheck precommit-setup precommit-run precommit-update precommit-clean

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
help:
	@echo "$(BLUE)Unified Command Toolkit for FastAPI Events App$(NC)"
	@echo ""
	@echo "$(YELLOW)Development & Docker Commands:$(NC)"
	@echo "  dev              - Start development environment with hot reload"
	@echo "  debug            - Start debug environment (waits for debugger)"
	@echo "  logs             - Show logs for dev service"
	@echo "  shell            - Access container shell"
	@echo "  db               - Access database shell"
	@echo "  status           - Show container status"
	@echo "  stop             - Stop all services"
	@echo "  clean            - Stop and remove all containers/volumes"
	@echo "  build            - Rebuild containers"
	@echo ""
	@echo "$(YELLOW)Testing Commands:$(NC)"
	@echo "  test             - Run all tests with docker-compose database"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-watch       - Run tests in watch mode"
	@echo "  test-quick       - Run quick tests (without docker database)"
	@echo "  test-file        - Run specific test file (usage: make test-file FILE=path/to/test.py)"
	@echo "  test-db-setup    - Set up test database only"
	@echo "  test-db-cleanup  - Clean up test database"
	@echo ""
	@echo "$(YELLOW)Development Setup:$(NC)"
	@echo "  install-dev      - Install development dependencies"
	@echo "  lint             - Run linting"
	@echo "  format           - Format code"
	@echo "  typecheck        - Run mypy type checking"
	@echo "  makemigrations   - Generate new database migrations"
	@echo "  migrate          - Apply database migrations"
	@echo ""
	@echo "$(YELLOW)Pre-commit Hooks:$(NC)"
	@echo "  precommit-setup  - Setup pre-commit hooks"
	@echo "  precommit-run    - Run pre-commit on all files"
	@echo "  precommit-update - Update pre-commit hooks"
	@echo "  precommit-clean  - Clean pre-commit cache"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make dev         # Start development environment"
	@echo "  make logs        # View logs"
	@echo "  make shell       # Access container"
	@echo "  make test        # Run all tests"
	@echo "  make test-file FILE=tests/test_main.py  # Run specific test"

# Development & Docker Commands
dev:
	@echo "$(BLUE)[INFO]$(NC) Starting development environment..."
	@docker-compose --profile dev up --build -d
	@echo "$(GREEN)[SUCCESS]$(NC) Development environment started!"
	@echo "$(BLUE)[INFO]$(NC) Application available at: http://localhost:8001"
	@echo "$(BLUE)[INFO]$(NC) View logs with: make logs"

debug:
	@echo "$(BLUE)[INFO]$(NC) Starting debug environment..."
	@echo "$(YELLOW)[WARNING]$(NC) This will wait for a debugger to attach on port 5678"
	@docker-compose --profile debug up --build

logs:
	@echo "$(BLUE)[INFO]$(NC) Showing logs for development service..."
	@docker-compose --profile dev logs -f app-dev

shell:
	@echo "$(BLUE)[INFO]$(NC) Accessing container shell..."
	@docker-compose --profile dev exec app-dev /bin/bash

db:
	@echo "$(BLUE)[INFO]$(NC) Accessing database shell..."
	@docker-compose --profile dev exec app-dev sqlite3 /app/data/app.db

status:
	@echo "$(BLUE)[INFO]$(NC) Container status:"
	@docker-compose --profile dev ps

stop:
	@echo "$(BLUE)[INFO]$(NC) Stopping all services..."
	@docker-compose --profile dev down
	@docker-compose --profile debug down
	@echo "$(GREEN)[SUCCESS]$(NC) All services stopped!"

clean:
	@echo "$(YELLOW)[WARNING]$(NC) This will remove all containers and volumes (including database data)"
	@read -p "Are you sure? (y/N): " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)[INFO]$(NC) Cleaning up..."; \
		docker-compose --profile dev down -v; \
		docker-compose --profile debug down -v; \
		docker system prune -f; \
		echo "$(GREEN)[SUCCESS]$(NC) Cleanup completed!"; \
	else \
		echo "$(BLUE)[INFO]$(NC) Cleanup cancelled."; \
	fi

build:
	@echo "$(BLUE)[INFO]$(NC) Rebuilding containers..."
	@docker-compose --profile dev build --no-cache
	@docker-compose --profile debug build --no-cache
	@echo "$(GREEN)[SUCCESS]$(NC) Containers rebuilt!"

# Testing Commands
test:
	@echo "$(BLUE)[INFO]$(NC) Running all tests with docker-compose database..."
	@python tests/run_tests.py

test-unit:
	@echo "$(BLUE)[INFO]$(NC) Running unit tests..."
	@python tests/run_tests.py -m "unit"

test-integration:
	@echo "$(BLUE)[INFO]$(NC) Running integration tests..."
	@python tests/run_tests.py -m "integration"

test-coverage:
	@echo "$(BLUE)[INFO]$(NC) Running tests with coverage..."
	@python tests/run_tests.py --cov-report=html --cov-report=term-missing

test-watch:
	@echo "$(BLUE)[INFO]$(NC) Running tests in watch mode..."
	@python tests/run_tests.py -f

test-quick:
	@echo "$(BLUE)[INFO]$(NC) Running quick tests (without docker database)..."
	@QUICK_TEST=true uv run pytest tests/ -v

test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "$(RED)[ERROR]$(NC) Please specify FILE=path/to/test_file.py"; \
		echo "Usage: make test-file FILE=tests/test_main.py"; \
		exit 1; \
	fi
	@echo "$(BLUE)[INFO]$(NC) Running test file: $(FILE)"
	@python tests/run_tests.py tests/$(FILE)

# Database management
test-db-setup:
	@echo "$(BLUE)[INFO]$(NC) Setting up test database..."
	@docker-compose -f tests/docker-compose.test.yml up -d postgres-test
	@echo "$(BLUE)[INFO]$(NC) Waiting for database to be ready..."
	@sleep 10
	@echo "$(GREEN)[SUCCESS]$(NC) Test database is ready!"

test-db-cleanup:
	@echo "$(BLUE)[INFO]$(NC) Cleaning up test database..."
	@docker-compose -f tests/docker-compose.test.yml down -v
	@echo "$(GREEN)[SUCCESS]$(NC) Test database cleaned up!"

# Development setup
install-dev:
	@echo "$(BLUE)[INFO]$(NC) Installing development dependencies..."
	@uv sync --group dev
	@echo "$(GREEN)[SUCCESS]$(NC) Development dependencies installed!"

# Code quality
lint:
	@echo "$(BLUE)[INFO]$(NC) Running linting..."
	@uv run ruff check .
	@echo "$(GREEN)[SUCCESS]$(NC) Linting completed!"

format:
	@echo "$(BLUE)[INFO]$(NC) Formatting code..."
	@uv run ruff format .
	@echo "$(GREEN)[SUCCESS]$(NC) Code formatting completed!"

typecheck:
	@echo "$(BLUE)[INFO]$(NC) Running mypy type checking..."
	@uv run mypy app/
	@echo "$(GREEN)[SUCCESS]$(NC) Type checking completed!"

# Database migration targets
makemigrations:
	@echo "$(BLUE)[INFO]$(NC) Generating new database migrations..."
	@docker-compose -f docker-compose.yml run --rm makemigrations
	@echo "$(GREEN)[SUCCESS]$(NC) Migrations generated!"

migrate:
	@echo "$(BLUE)[INFO]$(NC) Applying database migrations..."
	@docker-compose -f docker-compose.yml run --rm migrate
	@echo "$(GREEN)[SUCCESS]$(NC) Migrations applied!"
# Pre-commit hooks
precommit-setup:
	@echo "$(BLUE)[INFO]$(NC) Setting up pre-commit hooks..."
	@./scripts/setup-precommit.sh
	@echo "$(GREEN)[SUCCESS]$(NC) Pre-commit hooks setup completed!"

precommit-run:
	@echo "$(BLUE)[INFO]$(NC) Running pre-commit on all files..."
	@pre-commit run --all-files
	@echo "$(GREEN)[SUCCESS]$(NC) Pre-commit checks completed!"

precommit-update:
	@echo "$(BLUE)[INFO]$(NC) Updating pre-commit hooks..."
	@pre-commit autoupdate
	@echo "$(GREEN)[SUCCESS]$(NC) Pre-commit hooks updated!"

precommit-clean:
	@echo "$(BLUE)[INFO]$(NC) Cleaning pre-commit cache..."
	@pre-commit clean
	@echo "$(GREEN)[SUCCESS]$(NC) Pre-commit cache cleaned!"
