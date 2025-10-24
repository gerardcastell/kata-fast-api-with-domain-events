from app.contexts.customers.domain.entities.customer import Customer
from app.contexts.customers.domain.repositories.customer_repository import (
    CustomerRepository,
)


class CustomerCreator:
    def __init__(self, customer_repository: CustomerRepository, task_publisher):
        self.customer_repository = customer_repository
        self.task_publisher = task_publisher

    async def create(
        self,
        id: str | None = None,
        name: str | None = None,
        email: str | None = None,
        activePoliciesCount: int | None = None,
    ) -> Customer:
        # Only pass id if it's provided, let Customer generate it if None

        customer = Customer(id=id, name=name, email=email, activePoliciesCount=activePoliciesCount)
        await self.task_publisher(
            {
                "task": "send_email",
                "customer_id": customer.id,
            }
        )

        return await self.customer_repository.save(customer)
