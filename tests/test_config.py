import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentConfig(BaseSettings):
    """Test-specific configuration that overrides the default settings."""

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    app_title: str = Field("Insurance API - Test")
    debug: bool = Field(True)
    log_level: str = Field("DEBUG")
    environment: str = Field("test")

    # Use localhost instead of postgres hostname for tests
    sqlite_url: str = Field(default="sqlite+aiosqlite:///./test.db")
    postgres_url: str = Field(
        default="postgresql+asyncpg://postgres:1234@localhost:5433/cleverea_test"
    )
    psql_db_host: str = Field("localhost")
    psql_db_port: str = Field("5433")
    psql_db_database: str = Field("cleverea_test")
    psql_db_username: str = Field("postgres")
    psql_db_password: str = Field("1234")
    create_tables_on_startup: bool = Field(default=True)


# Override the settings for testing
def get_test_settings():
    return EnvironmentConfig()  # pyright: ignore[reportCallIssue]


# Set environment variables for testing
os.environ.update(
    {
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
)
