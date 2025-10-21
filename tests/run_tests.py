#!/usr/bin/env python3
"""Test runner script that integrates with docker-compose for database setup."""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def run_command(command, check=True, capture_output=False):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, check=check, capture_output=capture_output, text=True)
    return result


def wait_for_database(max_retries=30, delay=2):
    """Wait for the test database to be ready."""
    print("Waiting for test database to be ready...")

    for attempt in range(max_retries):
        try:
            # Try to connect to the database
            result = run_command(
                [
                    "docker",
                    "exec",
                    "events-with-fast-api-postgres-test-1",
                    "pg_isready",
                    "-U",
                    "postgres",
                    "-d",
                    "cleverea_test",
                ],
                check=False,
                capture_output=True,
            )

            if result.returncode == 0:
                print("Database is ready!")
                return True

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")

        time.sleep(delay)

    print("Database failed to become ready within the timeout period")
    return False


def setup_test_environment():
    """Set up the test environment with docker-compose."""
    print("Setting up test environment...")

    # Start the test database
    run_command(["docker-compose", "-f", "docker-compose.test.yml", "up", "-d", "postgres-test"])

    # Wait for database to be ready
    if not wait_for_database():
        print("Failed to start test database")
        return False

    # Run database migrations if needed
    print("Running database migrations...")
    try:
        run_command(["docker-compose", "-f", "docker-compose.test.yml", "run", "--rm", "migrate"])
    except subprocess.CalledProcessError:
        print("Warning: Database migrations failed, continuing with tests...")

    return True


def cleanup_test_environment():
    """Clean up the test environment."""
    print("Cleaning up test environment...")

    try:
        run_command(["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"])
    except subprocess.CalledProcessError:
        print("Warning: Failed to clean up test environment")


def run_pytest(pytest_args):
    """Run pytest with the given arguments."""
    print("Running pytest...")

    # Set environment variables for testing
    env = {
        **os.environ,
        "POSTGRES_URL": "postgresql+asyncpg://postgres:1234@localhost:5433/cleverea_test",
        "PSQL_DB_HOST": "localhost",
        "PSQL_DB_PORT": "5433",
        "PSQL_DB_DATABASE": "cleverea_test",
        "PSQL_DB_USERNAME": "postgres",
        "PSQL_DB_PASSWORD": "1234",
        "CREATE_TABLES_ON_STARTUP": "true",
        "DEBUG": "true",
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
    }

    # Run pytest
    result = subprocess.run(["uv", "run", "pytest"] + pytest_args, env=env)

    return result.returncode


def main():
    """Main function to run tests with docker-compose integration."""
    parser = argparse.ArgumentParser(description="Run tests with docker-compose database")
    parser.add_argument("pytest_args", nargs="*", help="Arguments to pass to pytest")
    parser.add_argument(
        "--no-setup",
        action="store_true",
        help="Skip database setup (assumes database is already running)",
    )
    parser.add_argument(
        "--no-cleanup", action="store_true", help="Skip database cleanup after tests"
    )

    args = parser.parse_args()

    # Change to project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)

    success = True

    try:
        # Set up test environment
        if not args.no_setup:
            if not setup_test_environment():
                print("Failed to set up test environment")
                return 1

        # Run tests
        exit_code = run_pytest(args.pytest_args)
        success = exit_code == 0

    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        success = False
    except Exception as e:
        print(f"Error running tests: {e}")
        success = False
    finally:
        # Clean up test environment
        if not args.no_cleanup:
            cleanup_test_environment()

    return 0 if success else 1


if __name__ == "__main__":
    import os

    sys.exit(main())
