from abc import ABC, abstractmethod

from app.shared.domain.event.domain_event import DomainEvent


class AsyncEventBus(ABC):
    @abstractmethod
    async def publish(self, events: list[DomainEvent]) -> None:
        pass
