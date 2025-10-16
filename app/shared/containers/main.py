from dependency_injector import containers, providers

from app.contexts.customers.container.customer_services import CustomerServices
from app.shared.containers.database import Database
from app.shared.infrastructure.db.postgresql_async import (
    PostgresDatabaseFactory,
)
from app.shared.infrastructure.db.sqlite_async import (
    SQLiteDatabaseFactory,
)


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    sqlite_database = providers.Singleton(
        Database, db_url=config.sqlite_url, database_factory=SQLiteDatabaseFactory
    )

    postgres_database = providers.Singleton(
        Database, db_url=config.postgres_url, database_factory=PostgresDatabaseFactory
    )

    database = postgres_database
    customer_services = providers.Container(
        CustomerServices, session_factory=database.provided.session_factory
    )
