"""Test configuration and fixtures for pytest."""

import asyncio
import os

# Set test environment variables - use SQLite for quick tests, PostgreSQL for integration tests
import sys

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.main import create_app
from app.shared.containers.database import Database
from app.shared.infrastructure.db.interface import AsyncDatabaseFactory
from test_config import get_test_settings

# Check if we're running quick tests (no database setup)
is_quick_test = os.environ.get("QUICK_TEST", "false").lower() == "true"

if is_quick_test:
    # Use SQLite for quick tests
    os.environ.update({
        "POSTGRES_URL": "sqlite+aiosqlite:///./test.db",
        "PSQL_DB_HOST": "localhost",
        "PSQL_DB_PORT": "5433",
        "PSQL_DB_DATABASE": "cleverea_test",
        "PSQL_DB_USERNAME": "postgres",
        "PSQL_DB_PASSWORD": "1234",
        "CREATE_TABLES_ON_STARTUP": "true",
        "DEBUG": "true",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG"
    })
else:
    # Use PostgreSQL for integration tests
    os.environ.update({
        "POSTGRES_URL": "postgresql+asyncpg://postgres:1234@localhost:5433/cleverea_test",
        "PSQL_DB_HOST": "localhost",
        "PSQL_DB_PORT": "5433",
        "PSQL_DB_DATABASE": "cleverea_test",
        "PSQL_DB_USERNAME": "postgres",
        "PSQL_DB_PASSWORD": "1234",
        "CREATE_TABLES_ON_STARTUP": "true",
        "DEBUG": "true",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG"
    })


@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test function."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Get test settings."""
    return get_test_settings()


@pytest.fixture(scope="function")
async def test_engine(test_settings):
    """Create a test database engine."""
    engine = create_async_engine(
        test_settings.postgres_url,
        echo=False,  # Disable echo to reduce noise
        future=True,
        pool_pre_ping=True,  # Ensure connections are valid
        pool_recycle=300,    # Recycle connections every 5 minutes
    )
    yield engine
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session_factory(test_engine):
    """Create a test session factory."""
    return sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest.fixture(scope="function")
async def test_db_session(test_session_factory):
    """Create a test database session for each test."""
    async with test_session_factory() as session:
        # Start a transaction that will be rolled back
        transaction = await session.begin()
        try:
            yield session
        finally:
            # Always rollback the transaction to clean up test data
            try:
                if not transaction.is_closed:
                    await transaction.rollback()
            except Exception:
                # Ignore rollback errors during cleanup
                pass


@pytest.fixture(scope="function")
async def test_database(test_settings):
    """Create a test database instance."""
    database_factory = AsyncDatabaseFactory()
    database = Database(
        db_url=test_settings.postgres_url,
        database_factory=database_factory
    )
    yield database
    await database.dispose()


@pytest.fixture(scope="function")
def test_client():
    """Create a test client for FastAPI."""
    test_settings = get_test_settings()
    app = create_app(custom_settings=test_settings)
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
async def async_test_client():
    """Create an async test client for FastAPI."""
    from httpx import ASGITransport
    test_settings = get_test_settings()
    app = create_app(custom_settings=test_settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database(test_settings):
    """Set up the test database once for all tests."""
    # Import here to avoid circular imports
    from sqlmodel import SQLModel
    
    # Create a session-scoped engine for setup/teardown
    engine = create_async_engine(
        test_settings.postgres_url,
        echo=False,
        future=True,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    try:
        # Create tables once
        async with engine.begin() as conn:
            # Import all models to ensure they're registered
            from app.contexts.customers.infrastructure.persistence.models.customer import (
                CustomerModel,  # noqa: F401
            )

            # Create all tables using SQLModel metadata
            await conn.run_sync(SQLModel.metadata.create_all)
        
        yield
        
    finally:
        # Clean up after all tests
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        await engine.dispose()


# Remove the cleanup_test_data fixture as it's redundant with the transaction rollback


# Markers for different test types
pytestmark = [
    pytest.mark.asyncio,
]
