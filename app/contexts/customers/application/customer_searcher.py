from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)


class CustomerSearcher:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    async def search_by_id(self, id: str) -> Customer:
        return await self.customer_repository.find_by_id(id)

    async def search_all(self) -> list[Customer]:
        return await self.customer_repository.find_all()
