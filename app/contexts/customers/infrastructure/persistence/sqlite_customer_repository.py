from contextlib import asynccontextmanager
from typing import Iterable

from sqlmodel import select

from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)
from app.shared.infrastructure.orm.sqlmodel import SQLModelRepository


class SQLiteCustomerRepository(CustomerRepository, SQLModelRepository):
    async def save(self, customer: Customer) -> Customer:
        async with self._session as session:
            session.add(customer)
            await session.flush()
            await session.refresh(customer)
            await session.commit()
            return customer

    async def find_by_id(self, id: str) -> Customer | None:
        async with self._session as session:
            return await session.get(Customer, id)

    async def find_all(self) -> Iterable[Customer]:
        async with self._session as session:
            res = await session.exec(select(Customer))
            return res.all()
