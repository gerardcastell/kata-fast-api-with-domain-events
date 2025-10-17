# Testing Guide

This project includes a comprehensive testing setup that integrates pytest with docker-compose for database testing.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.12+ with `uv` package manager
- Development dependencies installed (`make install-dev`)

## Quick Start

### Run All Tests

```bash
make test
```

### Run Specific Test Types

```bash
# Unit tests only
make test-unit

# Integration tests only
make test-integration

# Tests with coverage report
make test-coverage
```

### Run Tests Manually

```bash
# Using the test runner script
python run_tests.py

# Using pytest directly (requires database to be running)
uv run pytest

# Run specific test file
make test-file FILE=test_main.py
```

## Test Database Setup

The test setup uses a separate PostgreSQL database running in Docker:

- **Database**: `cleverea_test`
- **Port**: `5433` (to avoid conflicts with main database)
- **User**: `postgres`
- **Password**: `1234`

### Manual Database Management

```bash
# Start test database only
make test-db-setup

# Stop and clean up test database
make test-db-cleanup
```

## Test Configuration

### Pytest Configuration

The project uses pytest with the following configuration (in `pyproject.toml`):

- **AsyncIO support**: Automatic async test detection
- **Coverage reporting**: HTML, XML, and terminal reports
- **Test markers**: `unit`, `integration`, `slow`
- **Test discovery**: Automatically finds `test_*.py` files

### Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `test_client`: FastAPI TestClient for synchronous tests
- `async_test_client`: AsyncClient for asynchronous tests
- `test_db_session`: Database session for each test
- `test_database`: Database instance with proper cleanup
- `test_settings`: Test-specific configuration

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_unit_functionality():
    """Unit test that doesn't require external dependencies."""
    pass

@pytest.mark.integration
async def test_integration_with_database():
    """Integration test that uses the database."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Test that takes a long time to run."""
    pass
```

## Writing Tests

### Unit Tests

Unit tests should be fast and not require external dependencies:

```python
@pytest.mark.unit
def test_customer_creation():
    customer = Customer(name="John", email="john@example.com")
    assert customer.name == "John"
    assert customer.email == "john@example.com"
```

### Integration Tests

Integration tests can use the database and external services:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_customer_api_integration(async_test_client, test_db_session):
    response = await async_test_client.post("/customers/", json={
        "name": "John Doe",
        "email": "john@example.com"
    })
    assert response.status_code == 201
```

### Async Tests

Use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_functionality():
    result = await some_async_function()
    assert result is not None
```

## Test Database Management

### Automatic Setup

The test runner automatically:

1. Starts the test database container
2. Waits for the database to be ready
3. Runs database migrations
4. Executes tests
5. Cleans up the database container

### Manual Control

You can control the database setup manually:

```bash
# Skip database setup (assumes database is already running)
python run_tests.py --no-setup

# Skip database cleanup (useful for debugging)
python run_tests.py --no-cleanup
```

## Coverage Reports

Coverage reports are generated in multiple formats:

- **Terminal**: Shows coverage summary in the terminal
- **HTML**: Detailed HTML report in `htmlcov/` directory
- **XML**: XML report for CI/CD integration

View the HTML coverage report:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Run tests with XML coverage report
python run_tests.py --cov-report=xml

# Run only unit tests (faster)
python run_tests.py -m "unit"
```

## Troubleshooting

### Database Connection Issues

If you encounter database connection issues:

1. Ensure Docker is running
2. Check if the test database container is running: `docker ps`
3. Verify the database is ready: `docker logs events-with-fast-api-postgres-test-1`

### Test Failures

Common issues and solutions:

1. **Import errors**: Ensure all dependencies are installed with `make install-dev`
2. **Database errors**: Check that the test database is properly set up
3. **Async test issues**: Ensure tests are marked with `@pytest.mark.asyncio`

### Performance Issues

For faster test runs:

1. Use `make test-unit` for unit tests only
2. Use `make test-quick` for tests without database
3. Mark slow tests with `@pytest.mark.slow` and skip them with `-m "not slow"`

## Best Practices

1. **Test Isolation**: Each test should be independent and not rely on other tests
2. **Database Cleanup**: Use the provided fixtures for automatic cleanup
3. **Async Testing**: Use async fixtures for async functionality
4. **Test Markers**: Properly mark tests for easy filtering
5. **Coverage**: Aim for high test coverage, especially for critical business logic
6. **Fast Tests**: Keep unit tests fast, use integration tests sparingly
