import importlib
from pathlib import Path
import sys
import os
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

# Import settings to get database URL
from app.config.settings import settings

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


# Dynamically import all models from models folder
def import_models_from_folders(folders: list[str]):
    """
    Recursively import all Python modules in given folders so Alembic sees all models.
    """
    project_root = Path(__file__).parent.parent.resolve()  # adjust to project root
    for folder in folders:
        base_path = (project_root / folder).resolve()
        for path in base_path.rglob("*.py"):
            if path.name.startswith("__"):
                continue
            # make path relative to project root
            relative = path.relative_to(project_root)
            module_name = ".".join(relative.with_suffix("").parts)
            importlib.import_module(module_name)


model_folders = [
    "app/contexts/customers/infrastructure/persistence/models",
]
import_models_from_folders(model_folders)

database_url = settings.postgres_url  # or settings.sqlite_url

# Alembic Config object
config = context.config
config.set_main_option("sqlalchemy.url", database_url)

# Logging setup
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata for autogenerate
target_metadata = SQLModel.metadata


# ----- Offline migrations -----
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ----- Online migrations -----
def do_run_migrations(connection):
    """Run migrations using a sync connection (called from async)."""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(database_url, pool_pre_ping=True)

    async with connectable.connect() as connection:
        # Properly configure Alembic with the sync connection
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


# ----- Entry point -----
if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
