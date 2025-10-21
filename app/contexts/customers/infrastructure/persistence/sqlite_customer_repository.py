from typing import Callable, Iterable

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)
from app.contexts.customers.infrastructure.persistence.models.customer import (
    CustomerModel,
)


class PostgreSQLCustomerRepository(CustomerRepository):
    def __init__(self, session_factory: Callable[[], AsyncSession]):
        self.session_factory = session_factory

    async def save(self, customer: Customer) -> Customer:
        async with self.session_factory() as session:
            # Convert domain entity to persistence model
            customer_model = CustomerModel(
                id=customer.id,
                name=customer.name,
                email=customer.email,
                activePoliciesCount=customer.activePoliciesCount,
            )
            session.add(customer_model)
            await session.flush()
            await session.refresh(customer_model)

            # Convert back to domain entity
            return Customer(
                id=customer_model.id,
                name=customer_model.name,
                email=customer_model.email,
                activePoliciesCount=customer_model.activePoliciesCount,
            )

    async def find_by_id(self, id: str) -> Customer | None:
        async with self.session_factory() as session:
            customer_model = await session.get(CustomerModel, id)
            if customer_model is None:
                return None

            # Convert persistence model to domain entity
            return Customer(
                id=customer_model.id,
                name=customer_model.name,
                email=customer_model.email,
                activePoliciesCount=customer_model.activePoliciesCount,
            )

    async def find_all(self) -> Iterable[Customer]:
        async with self.session_factory() as session:
            res = await session.exec(select(CustomerModel))
            customer_models = res.all()

            # Convert persistence models to domain entities
            return [
                Customer(
                    id=str(customer_model.id),
                    name=customer_model.name,
                    email=customer_model.email,
                    activePoliciesCount=customer_model.activePoliciesCount,
                )
                for customer_model in customer_models
            ]
