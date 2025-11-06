from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    app_title: str = Field("Insurance API")
    debug: bool = Field(False)
    log_level: str = Field("INFO")
    environment: str = Field("development")

    sqlite_url: str = Field(default="sqlite+aiosqlite:///./app.db")
    postgres_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/cleverea"
    )
    psql_db_host: str = Field("postgres")
    psql_db_port: str = Field("5432")
    psql_db_database: str = Field("cleverea")
    psql_db_username: str = Field("postgres")
    psql_db_password: str = Field("1234")
    create_tables_on_startup: bool = Field(default=False)

    # SQS Configuration
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_region: str = Field(default="us-east-1")
    aws_endpoint_url: str = Field(default="")
    sqs_queue_url: str = Field(default="")
    sqs_max_messages: int = Field(default=10)
    sqs_wait_time_seconds: int = Field(default=20)
    sqs_visibility_timeout: int = Field(default=300)
    sqs_max_receive_count: int = Field(default=1)


settings = Config()  # pyright: ignore[reportCallIssue]
