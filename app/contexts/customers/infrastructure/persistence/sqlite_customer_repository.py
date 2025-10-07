from sqlmodel import select
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)
from app.contexts.customers.domain.entities.customer import Customer
from app.shared.infrastructure.orm.sqlmodel import SQLModelRepository
from typing import Iterable


class SQLiteCustomerRepository(CustomerRepository, SQLModelRepository):
    async def save(self, customer: Customer) -> Customer:
        self._session.add(customer)
        await self._session.flush()
        await self._session.refresh(customer)
        return customer

    async def find_by_id(self, id: str) -> Customer | None:
        return await self._session.get(Customer, id)

    async def find_all(self) -> Iterable[Customer]:
        res = await self._session.exec(select(Customer))
        return res.all()
