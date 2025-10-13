from dependency_injector import containers, providers

from app.contexts.customers.container.customer_services import CustomerServices
from app.shared.containers.database import Database


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    database = providers.Singleton(Database, db_url=config.sqlite_url)

    customer_services = providers.Container(
        CustomerServices, session_factory=database.provided.session_factory
    )
