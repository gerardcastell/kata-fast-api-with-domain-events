from dependency_injector import containers, providers

from app.contexts.customers.container.customer_services import CustomerServices
from app.shared.containers.database import Database
from app.shared.infrastructure.db.postgresql_async import (
    PostgresDatabaseFactory,
)
from app.shared.infrastructure.db.sqlite_async import (
    SQLiteDatabaseFactory,
)
from app.shared.infrastructure.event.in_memory_event_bus import InMemoryEventBus
from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.dispatcher import TaskDispatcher


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    # Database
    sqlite_database = providers.Singleton(
        Database,
        db_url=config.sqlite_url,
        database_factory=providers.Factory(SQLiteDatabaseFactory),
    )

    postgres_database = providers.Singleton(
        Database,
        db_url=config.postgres_url,
        database_factory=providers.Factory(PostgresDatabaseFactory),
    )

    database = postgres_database

    # Event Bus
    event_bus = providers.Singleton(InMemoryEventBus)

    # SQS Services
    sqs_client = providers.Singleton(
        SQSClient,
        queue_url=config.sqs_queue_url,
    )

    task_dispatcher = providers.Singleton(
        TaskDispatcher,
        sqs_client=sqs_client,
    )

    customer_services = providers.Container(
        CustomerServices, session_factory=database.provided.session_factory
    )
