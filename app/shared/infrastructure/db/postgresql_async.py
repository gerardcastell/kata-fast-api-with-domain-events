from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.infrastructure.db.interface import AsyncDatabaseFactory


class PostgresDatabaseFactory(AsyncDatabaseFactory):
    def build_async_engine(url: str) -> AsyncEngine:
        """
        Create an async SQLAlchdemy engine for PostgreSQL.
        """
        engine = create_async_engine(
            url,
            echo=False,  # Set True for SQL logging
            future=True,
            pool_pre_ping=True,  # Detect broken connections
        )

        return engine

    def build_async_session_factory(
        engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        """
        Create an async session factory for PostgreSQL.
        """
        return async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            future=True,
        )
