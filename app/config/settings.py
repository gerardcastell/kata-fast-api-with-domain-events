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

    RABBITMQ_USER: str = Field("guest")
    RABBITMQ_PASSWORD: str = Field("guest")
    RABBITMQ_HOST: str = Field("rabbitmq")
    RABBITMQ_PORT: str = Field("5672")
    RABBITMQ_VHOST: str = Field("")
    RABBITMQ_QUEUE: str = Field("main_queue")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Config()
