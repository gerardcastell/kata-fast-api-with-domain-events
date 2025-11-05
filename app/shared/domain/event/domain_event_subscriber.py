from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.shared.domain.event.domain_event import DomainEvent

TDomainEvent = TypeVar("TDomainEvent", bound=DomainEvent)


class DomainEventSubscriber(Generic[TDomainEvent], ABC):
    @abstractmethod
    async def on(self, event: TDomainEvent) -> None:
        pass

    @abstractmethod
    def subscribed_to(self) -> list[TDomainEvent]:
        pass
