import asyncio

from app.shared.domain.event.domain_event import DomainEvent
from app.shared.domain.event.domain_event_subscriber import DomainEventSubscriber
from app.shared.domain.event.event_bus import AsyncEventBus


class InMemoryEventBus(AsyncEventBus):
    def __init__(self, subscribers: list[DomainEventSubscriber] | None = None):
        self._subscriptions: dict[DomainEvent, list[DomainEventSubscriber]] = {}
        if subscribers:
            self._register_subscribers(subscribers)

    async def publish(self, events: list[DomainEvent]) -> None:
        """Publish a single event to all subscribed handlers."""
        executions = [
            subscriber.on(event)
            for event in events
            for subscriber in self._subscriptions.get(event, [])
        ]
        if executions:
            await asyncio.gather(*executions)

    def _register_subscribers(self, subscribers: list[DomainEventSubscriber]) -> None:
        """Register subscribers. Thread-safe for async use."""
        for subscriber in subscribers:
            for event in subscriber.subscribed_to():
                self._subscriptions.setdefault(event, []).append(subscriber)
