# Unified Command Toolkit for events-with-fast-api project

.PHONY: help dev debug logs shell db status stop clean build test test-unit test-integration test-coverage test-watch test-db-setup test-db-cleanup install-dev lint format makemigrations migrate test-quick test-file typecheck precommit-setup precommit-run precommit-update precommit-clean localstack localstack-logs localstack-stop sqs-test lambda-deploy lambda-test lambda-logs lambda-container-logs lambda-invoke lambda-cleanup worker worker-logs worker-stop worker-shell worker-example

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
	@echo "$(YELLOW)LocalStack SQS Commands:$(NC)"
	@echo "  localstack       - Start LocalStack SQS service"
	@echo "  localstack-logs  - Show LocalStack logs"
	@echo "  localstack-stop  - Stop LocalStack service"
	@echo "  sqs-test         - Test SQS functionality"
	@echo ""
	@echo "$(YELLOW)Lambda Testing Commands:$(NC)"
	@echo "  lambda-deploy         - Deploy Lambda function to LocalStack (requires Pro)"
	@echo "  lambda-test           - Test Lambda with SQS trigger"
	@echo "  lambda-logs           - View Lambda CloudWatch logs"
	@echo "  lambda-container-logs - View Lambda container logs (more reliable)"
	@echo "  lambda-invoke         - Invoke Lambda directly with test event"
	@echo "  lambda-cleanup        - Remove Lambda function from LocalStack"
	@echo ""
	@echo "$(YELLOW)  Note:$(NC) Container images require LocalStack Pro (Community uses worker mode)"
	@echo ""
	@echo "$(YELLOW)Worker Commands:$(NC)"
	@echo "  worker           - Start SQS worker service"
	@echo "  worker-logs      - Show worker logs"
	@echo "  worker-stop      - Stop worker service"
	@echo "  worker-shell     - Access worker container shell"
	@echo "  worker-example   - Run worker example script"
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
	@docker-compose up app-dev --build -d
	@echo "$(GREEN)[SUCCESS]$(NC) Development environment started!"
	@echo "$(BLUE)[INFO]$(NC) Application available at: http://localhost:8001"
	@echo "$(BLUE)[INFO]$(NC) View logs with: make logs"

debug:
	@echo "$(BLUE)[INFO]$(NC) Starting debug environment..."
	@echo "$(YELLOW)[WARNING]$(NC) This will wait for a debugger to attach on port 5678"
	@docker-compose up app-debug --build

logs:
	@echo "$(BLUE)[INFO]$(NC) Showing logs for development service..."
	@docker-compose logs -f app-dev

shell:
	@echo "$(BLUE)[INFO]$(NC) Accessing container shell..."
	@docker-compose exec app-dev /bin/bash

db:
	@echo "$(BLUE)[INFO]$(NC) Accessing database shell..."
	@docker-compose exec postgres psql -U postgres -d cleverea

status:
	@echo "$(BLUE)[INFO]$(NC) Container status:"
	@docker-compose ps

stop:
	@echo "$(BLUE)[INFO]$(NC) Stopping all services..."
	@docker-compose down app-dev
	@docker-compose down app-debug
	@echo "$(GREEN)[SUCCESS]$(NC) All services stopped!"

clean:
	@echo "$(YELLOW)[WARNING]$(NC) This will remove all containers and volumes (including database data)"
	@read -p "Are you sure? (y/N): " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(BLUE)[INFO]$(NC) Cleaning up..."; \
		docker-compose down app-dev -v; \
		docker-compose down app-debug -v; \
		docker system prune -f; \
		echo "$(GREEN)[SUCCESS]$(NC) Cleanup completed!"; \
	else \
		echo "$(BLUE)[INFO]$(NC) Cleanup cancelled."; \
	fi

build:
	@echo "$(BLUE)[INFO]$(NC) Rebuilding containers..."
	@docker-compose build app-dev --no-cache
	@docker-compose build app-debug --no-cache
	@echo "$(GREEN)[SUCCESS]$(NC) Containers rebuilt!"

# LocalStack SQS Commands
localstack:
	@echo "$(BLUE)[INFO]$(NC) Starting LocalStack SQS service..."
	@docker-compose up localstack --build -d
	@echo "$(GREEN)[SUCCESS]$(NC) LocalStack started!"
	@echo "$(BLUE)[INFO]$(NC) LocalStack available at: http://localhost:4566"
	@echo "$(BLUE)[INFO]$(NC) View logs with: make localstack-logs"

localstack-logs:
	@echo "$(BLUE)[INFO]$(NC) Showing LocalStack logs..."
	@docker-compose logs -f localstack

localstack-stop:
	@echo "$(BLUE)[INFO]$(NC) Stopping LocalStack service..."
	@docker-compose down localstack
	@echo "$(GREEN)[SUCCESS]$(NC) LocalStack stopped!"

sqs-test:
	@echo "$(BLUE)[INFO]$(NC) Testing SQS functionality..."
	@echo "$(BLUE)[INFO]$(NC) Running Python integration test..."
	@uv run python scripts/test_sqs_localstack.py

# Lambda Testing Commands
lambda-deploy:
	@echo "$(BLUE)[INFO]$(NC) Deploying Lambda function to LocalStack..."
	@./scripts/deploy-lambda-localstack.sh

lambda-test:
	@echo "$(BLUE)[INFO]$(NC) Testing Lambda function with LocalStack..."
	@./scripts/test-lambda-localstack.sh

lambda-logs:
	@echo "$(BLUE)[INFO]$(NC) Fetching Lambda logs from LocalStack..."
	@echo "$(BLUE)[INFO]$(NC) Checking if Lambda function exists..."
	@if awslocal lambda get-function --function-name events-sqs-processor >/dev/null 2>&1; then \
		echo "$(GREEN)[SUCCESS]$(NC) Lambda function found"; \
		echo "$(BLUE)[INFO]$(NC) Checking for log groups..."; \
		if awslocal logs describe-log-groups --log-group-name-prefix "/aws/lambda/events-sqs-processor" >/dev/null 2>&1; then \
			echo "$(GREEN)[SUCCESS]$(NC) Log group found, fetching logs..."; \
			awslocal logs tail /aws/lambda/events-sqs-processor --since 10m --follow || echo "$(YELLOW)[WARNING]$(NC) No logs available or log streaming not supported"; \
		else \
			echo "$(YELLOW)[WARNING]$(NC) No log group found. Lambda hasn't been invoked yet."; \
			echo "$(BLUE)[INFO]$(NC) Try: make lambda-invoke or send messages to SQS"; \
		fi; \
	else \
		echo "$(RED)[ERROR]$(NC) Lambda function 'events-sqs-processor' not found"; \
		echo "$(BLUE)[INFO]$(NC) Deploy Lambda first: make lambda-deploy"; \
	fi

lambda-invoke:
	@echo "$(BLUE)[INFO]$(NC) Invoking Lambda function directly..."
	@echo '{"Records":[{"body":"{\"task_id\":\"test-123\",\"task_type\":\"data_processing\",\"priority\":\"normal\",\"payload\":{\"data\":[1,2,3]},\"retry_count\":0,\"max_retries\":3,\"delay_seconds\":0,\"timestamp\":\"2025-01-01T00:00:00Z\"}"}]}' | \
	awslocal lambda invoke --function-name events-sqs-processor --cli-binary-format raw-in-base64-out /tmp/lambda-out.json && \
	echo "$(GREEN)[SUCCESS]$(NC) Response:" && cat /tmp/lambda-out.json && echo ""

lambda-container-logs:
	@echo "$(BLUE)[INFO]$(NC) Finding Lambda container..."
	@LAMBDA_CONTAINER=$$(docker ps --filter "name=lambda" --format "{{.Names}}" | head -1); \
	if [ -n "$$LAMBDA_CONTAINER" ]; then \
		echo "$(GREEN)[SUCCESS]$(NC) Found Lambda container: $$LAMBDA_CONTAINER"; \
		echo "$(BLUE)[INFO]$(NC) Streaming logs (Ctrl+C to stop)..."; \
		docker logs -f $$LAMBDA_CONTAINER; \
	else \
		echo "$(YELLOW)[WARNING]$(NC) No Lambda container found"; \
		echo "$(BLUE)[INFO]$(NC) Lambda may not be running or hasn't been invoked yet"; \
		echo "$(BLUE)[INFO]$(NC) Try: make lambda-invoke or send messages to SQS"; \
	fi

lambda-cleanup:
	@echo "$(BLUE)[INFO]$(NC) Removing Lambda function from LocalStack..."
	@awslocal lambda delete-function --function-name events-sqs-processor || echo "$(YELLOW)[WARNING]$(NC) Function may not exist"
	@echo "$(GREEN)[SUCCESS]$(NC) Lambda function removed!"

# Worker Commands
worker:
	@echo "$(BLUE)[INFO]$(NC) Starting SQS worker service..."
	@docker-compose up worker --build -d
	@echo "$(GREEN)[SUCCESS]$(NC) Worker started!"
	@echo "$(BLUE)[INFO]$(NC) View logs with: make worker-logs"

worker-logs:
	@echo "$(BLUE)[INFO]$(NC) Showing worker logs..."
	@docker-compose logs -f worker

worker-stop:
	@echo "$(BLUE)[INFO]$(NC) Stopping worker service..."
	@docker-compose down worker
	@echo "$(GREEN)[SUCCESS]$(NC) Worker stopped!"

worker-shell:
	@echo "$(BLUE)[INFO]$(NC) Accessing worker container shell..."
	@docker-compose exec worker /bin/bash

worker-example:
	@echo "$(BLUE)[INFO]$(NC) Running worker example..."
	@uv run python scripts/worker_example.py

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
