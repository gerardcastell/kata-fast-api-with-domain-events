from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
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

    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    SQS_QUEUE: str = Field(default="test-queue", env="SQS_QUEUE")
    SQS_QUEUE_URL: str = Field(default="http://localstack:4566/000000000000/test-queue", env="SQS_QUEUE_URL")
    SQS_BROKER_URL: str = Field(default="sqs://test:test@localstack:4566/", env="SQS_BROKER_URL")
    AWS_ACCESS_KEY_ID: str = Field(default="test", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="test", env="AWS_SECRET_ACCESS_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Config()
