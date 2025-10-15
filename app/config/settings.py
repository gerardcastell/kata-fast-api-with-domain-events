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
    create_tables_on_startup: bool = Field(default=False)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Config()
