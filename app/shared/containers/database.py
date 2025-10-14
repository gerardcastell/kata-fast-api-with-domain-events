from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession


class Database:
    def __init__(
        self,
        db_url: str,
        async_engine: AsyncEngine,
        async_session: async_sessionmaker[AsyncSession],
    ):
        self._db_url = db_url

        # Single engine instance reused across the app lifetime
        self._async_engine = async_engine(url=self._db_url)
        self._session_factory = async_session(engine=self._async_engine)

    @asynccontextmanager
    async def session_factory(self):
        """Context manager for database sessions with proper cleanup"""
        session = self._session_factory()
        try:
            yield session
            print("committing session")
            await session.commit()
        except Exception:
            print("rolling back session")
            await session.rollback()
            raise
        finally:
            print("Closing session")
            await session.close()

    async def dispose(self):
        await self._async_engine.dispose()
