from contextlib import asynccontextmanager

from app.shared.infrastructure.db.interface import AsyncDatabaseFactory


class Database:
    def __init__(self, db_url: str, database_factory: AsyncDatabaseFactory):
        self._db_url = db_url

        # Single engine instance reused across the app lifetime
        self._async_engine = database_factory.build_async_engine(url=self._db_url)
        self._session_factory = database_factory.build_async_session_factory(
            engine=self._async_engine
        )

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
