from contextlib import asynccontextmanager

from dependency_injector import containers, providers

from app.shared.infrastructure.db.sqlite_async import (
    build_engine,
    build_session_factory,
)


class Persistence(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()

    def _get_database_url(core_container):
        return core_container.config.database.url()
    
    engine = providers.Singleton(
        build_engine,
        url=providers.Callable(_get_database_url, core_container=core),
    )

    session_factory = providers.Singleton(build_session_factory, engine=engine)

    @asynccontextmanager
    async def _session(sf):
        async with sf() as s:
            try:
                yield s
                await s.commit()
            except Exception:
                await s.rollback()
                raise

    session = providers.Resource(
        _session, sf=session_factory
    )  # Resource provides a per-use context managed session
