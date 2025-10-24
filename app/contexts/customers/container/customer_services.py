from dependency_injector import containers, providers
from sqlmodel.ext.asyncio.session import AsyncSession

from app.broker import publish_task
from app.contexts.customers.application.customer_creator import CustomerCreator
from app.contexts.customers.application.customer_searcher import CustomerSearcher
from app.contexts.customers.infrastructure.persistence.sqlite_customer_repository import (
    PostgreSQLCustomerRepository,
)


class CustomerServices(containers.DeclarativeContainer):
    session_factory = providers.Dependency[AsyncSession]()

    customer_repository = providers.Factory(
        PostgreSQLCustomerRepository, session_factory=session_factory
    )

    customer_creator = providers.Factory(
        CustomerCreator, customer_repository=customer_repository, task_publisher=publish_task
    )
    customer_searcher = providers.Factory(CustomerSearcher, customer_repository=customer_repository)
