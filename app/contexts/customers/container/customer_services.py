from dependency_injector import containers, providers

from app.contexts.customers.application.customer_creator import CustomerCreator
from app.contexts.customers.application.customer_searcher import CustomerSearcher
from app.contexts.customers.infrastructure.persistence.sqlite_customer_repository import (
    SQLiteCustomerRepository,
)


class CustomerServices(containers.DeclarativeContainer):
    session_factory = providers.Dependency()

    customer_repository = providers.Factory(
        SQLiteCustomerRepository, session_factory=session_factory
    )

    customer_creator = providers.Factory(
        CustomerCreator, customer_repository=customer_repository
    )
    customer_searcher = providers.Factory(
        CustomerSearcher, customer_repository=customer_repository
    )
