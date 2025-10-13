from pydantic import Field
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    app_title: str = Field('Insurance API')
    debug: bool = Field(False)
    log_level: str = Field('INFO')
    environment: str = Field('development')

    sqlite_url: str = Field()
    create_tables_on_startup: bool = False


settings = Config(_env_file='.env', _env_file_encoding='utf-8')