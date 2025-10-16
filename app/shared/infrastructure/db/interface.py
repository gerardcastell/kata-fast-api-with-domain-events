from typing import Protocol

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession


class AsyncDatabaseFactory(Protocol):
    """
    Defines the interface for building async SQLAlchemy engine and session factory.
    """

    def build_async_engine(self, url: str) -> AsyncEngine: ...

    def build_async_session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]: ...
