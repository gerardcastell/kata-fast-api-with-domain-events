from dependency_injector import containers, providers

from app.contexts.customers.container.customer_services import CustomerServices
from app.shared.containers.database import Database
from app.shared.infrastructure.db.sqlite_async import (
    build_async_engine as sqlite_build_async_engine,
    build_async_session_factory as sqlite_build_async_session_factory,
)
from app.shared.infrastructure.db.postgresql_async import (
    build_async_engine as postgres_build_async_engine,
    build_async_session_factory as postgres_build_async_session_factory,
)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    sqlite_database = providers.Singleton(
        Database,
        db_url=config.sqlite_url,
        async_engine=sqlite_build_async_engine,
        async_session=sqlite_build_async_session_factory,
    )

    postgres_database = providers.Singleton(
        Database,
        db_url=config.postgres_url,
        async_engine=postgres_build_async_engine,
        async_session=postgres_build_async_session_factory,
    )
    database = postgres_database
    customer_services = providers.Container(
        CustomerServices, session_factory=database.provided.session_factory
    )
