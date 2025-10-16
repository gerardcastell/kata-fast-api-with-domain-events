from abc import ABC, abstractmethod
from typing import Iterable

from ..entities.customer import Customer


class CustomerRepository(ABC):
    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        pass

    @abstractmethod
    async def find_by_id(self, id: str) -> Customer | None:
        pass

    @abstractmethod
    async def find_all(self) -> Iterable[Customer]:
        pass
