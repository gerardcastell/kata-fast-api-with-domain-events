# Makefile for events-with-fast-api project

.PHONY: help test test-unit test-integration test-coverage test-watch test-db-setup test-db-cleanup install-dev lint format makemigrations migrate test-quick test-quick-all

# Default target
help:
	@echo "Available targets:"
	@echo "  test              - Run all tests with docker-compose database"
	@echo "  test-unit         - Run unit tests only"
	@echo "  test-integration  - Run integration tests only"
	@echo "  test-coverage     - Run tests with coverage report"
	@echo "  test-watch        - Run tests in watch mode"
	@echo "  test-db-setup     - Set up test database only"
	@echo "  test-db-cleanup   - Clean up test database"
	@echo "  install-dev       - Install development dependencies"
	@echo "  lint              - Run linting"
	@echo "  format            - Format code"
	@echo "  makemigrations    - Generate new database migrations"
	@echo "  migrate           - Apply database migrations"

# Test targets
test:
	@echo "Running all tests with docker-compose database..."
	python run_tests.py

test-unit:
	@echo "Running unit tests..."
	python run_tests.py -m "unit"

test-integration:
	@echo "Running integration tests..."
	python run_tests.py -m "integration"

test-coverage:
	@echo "Running tests with coverage..."
	python run_tests.py --cov-report=html --cov-report=term-missing

test-watch:
	@echo "Running tests in watch mode..."
	python run_tests.py -f

# Database management
test-db-setup:
	@echo "Setting up test database..."
	docker-compose -f docker-compose.test.yml up -d postgres-test
	@echo "Waiting for database to be ready..."
	@sleep 10
	@echo "Test database is ready!"

test-db-cleanup:
	@echo "Cleaning up test database..."
	docker-compose -f docker-compose.test.yml down -v

# Development setup
install-dev:
	@echo "Installing development dependencies..."
	uv sync --group dev

# Code quality
lint:
	@echo "Running linting..."
	uv run ruff check .

format:
	@echo "Formatting code..."
	uv run ruff format .

# Quick test without docker (for development)
test-quick:
	@echo "Running quick tests (without docker database)..."
	QUICK_TEST=true uv run pytest tests/ -v

# Run specific test file
test-file:
	@echo "Usage: make test-file FILE=path/to/test_file.py"
	@if [ -z "$(FILE)" ]; then echo "Please specify FILE=path/to/test_file.py"; exit 1; fi
	python run_tests.py tests/$(FILE)

# Database migration targets
makemigrations:
	@echo "Generating new database migrations..."
	docker-compose -f docker-compose.test.yml run --rm makemigrations

migrate:
	@echo "Applying database migrations..."
	docker-compose -f docker-compose.test.yml run --rm migrate
