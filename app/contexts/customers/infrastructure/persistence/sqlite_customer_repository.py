from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)


class SQLiteCustomerRepository(CustomerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _with_session(self, ):
        async with self.session as session:
            yield session
    
    async def save(self, customer: Customer, ) -> Customer:
        async with self.session as session:
            session.add(customer)
            await session.flush()
            await session.refresh(customer)
            return customer

    async def find_by_id(self, id: str, ) -> Customer | None:
        async with self.session as session:
            return await session.get(Customer, id)

    async def find_all(self, ) -> Iterable[Customer]:
        async with self.session as session:
            res = await session.exec(select(Customer))
        return res.all()
