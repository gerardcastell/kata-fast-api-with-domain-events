from typing import Iterable

from sqlmodel import select

from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)


class SQLiteCustomerRepository(CustomerRepository):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def save(self, customer: Customer) -> Customer:
        async with self.session_factory() as session:
            session.add(customer)
            await session.flush()
            await session.refresh(customer)
            return customer

    async def find_by_id(self, id: str) -> Customer | None:
        async with self.session_factory() as session:
            return await session.get(Customer, id)

    async def find_all(self) -> Iterable[Customer]:
        async with self.session_factory() as session:
            res = await session.exec(select(Customer))
            return res.all()
