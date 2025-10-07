from typing import Optional

from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)


class CustomerCreator:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    async def create(
        self,
        id: Optional[str] = None,
        name: str = None,
        email: str = None,
        activePoliciesCount: Optional[int] = 0,
    ) -> Customer:
        # Only pass id if it's provided, let Customer generate it if None
        customer_kwargs = {"name": name, "email": email, "activePoliciesCount": activePoliciesCount}
        if id is not None:
            customer_kwargs["id"] = id
        customer = Customer(**customer_kwargs)
        return await self.customer_repository.save(customer)
