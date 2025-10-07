from typing import Optional
from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)


class CustomerCreator:
    def __init__(self, customer_repository: CustomerRepository):
        self.customer_repository = customer_repository

    def create(
        self,
        id: Optional[str],
        name: str,
        email: str,
        activePoliciesCount: Optional[int],
    ) -> Customer:
        customer = Customer(
            id=id, name=name, email=email, activePoliciesCount=activePoliciesCount
        )
        return self.customer_repository.save(customer)
