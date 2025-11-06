"""Unit tests for InMemoryEventBus."""

import pytest

from app.shared.domain.event.domain_event import DomainEvent
from app.shared.domain.event.domain_event_subscriber import DomainEventSubscriber
from app.shared.infrastructure.event.in_memory_event_bus import InMemoryEventBus


# Test event classes
class SampleEvent1(DomainEvent):
    """Sample event class 1."""


class SampleEvent2(DomainEvent):
    """Sample event class 2."""


class SampleEvent3(DomainEvent):
    """Sample event class 3."""


# Test subscriber classes
class SampleSubscriber1(DomainEventSubscriber[SampleEvent1]):
    """Sample subscriber for SampleEvent1."""

    def __init__(self):
        self.handled_events = []

    async def on(self, event: SampleEvent1) -> None:
        self.handled_events.append(event)

    def subscribed_to(self) -> list[type[SampleEvent1]]:
        return [SampleEvent1]


class SampleSubscriber2(DomainEventSubscriber[SampleEvent2]):
    """Sample subscriber for SampleEvent2."""

    def __init__(self):
        self.handled_events = []

    async def on(self, event: SampleEvent2) -> None:
        self.handled_events.append(event)

    def subscribed_to(self) -> list[type[SampleEvent2]]:
        return [SampleEvent2]


class SampleSubscriberMultiple(DomainEventSubscriber[DomainEvent]):
    """Sample subscriber for multiple event types."""

    def __init__(self):
        self.handled_events = []

    async def on(self, event: DomainEvent) -> None:
        self.handled_events.append(event)

    def subscribed_to(self) -> list[type[DomainEvent]]:
        return [SampleEvent1, SampleEvent2]


class SampleSubscriber3(DomainEventSubscriber[SampleEvent3]):
    """Sample subscriber for SampleEvent3."""

    def __init__(self):
        self.handled_events = []

    async def on(self, event: SampleEvent3) -> None:
        self.handled_events.append(event)

    def subscribed_to(self) -> list[type[SampleEvent3]]:
        return [SampleEvent3]


class TestInMemoryEventBus:
    """Test suite for InMemoryEventBus."""

    def test_init_without_subscribers(self):
        """Test initialization without subscribers."""
        bus = InMemoryEventBus()
        assert bus._subscriptions == {}

    def test_init_with_subscribers(self):
        """Test initialization with subscribers."""
        subscriber1 = SampleSubscriber1()
        subscriber2 = SampleSubscriber2()
        bus = InMemoryEventBus(subscribers=[subscriber1, subscriber2])

        assert SampleEvent1 in bus._subscriptions
        assert SampleEvent2 in bus._subscriptions
        assert len(bus._subscriptions[SampleEvent1]) == 1
        assert len(bus._subscriptions[SampleEvent2]) == 1
        assert subscriber1 in bus._subscriptions[SampleEvent1]
        assert subscriber2 in bus._subscriptions[SampleEvent2]

    def test_init_with_subscriber_multiple_events(self):
        """Test initialization with subscriber that handles multiple events."""
        subscriber = SampleSubscriberMultiple()
        bus = InMemoryEventBus(subscribers=[subscriber])

        assert SampleEvent1 in bus._subscriptions
        assert SampleEvent2 in bus._subscriptions
        assert subscriber in bus._subscriptions[SampleEvent1]
        assert subscriber in bus._subscriptions[SampleEvent2]

    @pytest.mark.asyncio
    async def test_publish_no_subscribers(self):
        """Test publishing events when there are no subscribers."""
        bus = InMemoryEventBus()
        event1 = SampleEvent1()  # type: ignore[call-arg]
        event2 = SampleEvent2()  # type: ignore[call-arg]

        # Should not raise any errors
        await bus.publish([event1, event2])

    @pytest.mark.asyncio
    async def test_publish_single_event_single_subscriber(self):
        """Test publishing a single event to a single subscriber."""
        subscriber = SampleSubscriber1()
        bus = InMemoryEventBus(subscribers=[subscriber])

        event = SampleEvent1()  # type: ignore[call-arg]
        await bus.publish([event])

        assert len(subscriber.handled_events) == 1
        assert subscriber.handled_events[0] == event

    @pytest.mark.asyncio
    async def test_publish_multiple_events_single_subscriber(self):
        """Test publishing multiple events to a single subscriber."""
        subscriber = SampleSubscriberMultiple()
        bus = InMemoryEventBus(subscribers=[subscriber])

        event1 = SampleEvent1()  # type: ignore[call-arg]
        event2 = SampleEvent2()  # type: ignore[call-arg]
        await bus.publish([event1, event2])

        assert len(subscriber.handled_events) == 2
        assert event1 in subscriber.handled_events
        assert event2 in subscriber.handled_events

    @pytest.mark.asyncio
    async def test_publish_single_event_multiple_subscribers(self):
        """Test publishing a single event to multiple subscribers."""
        subscriber1 = SampleSubscriber1()
        subscriber2 = SampleSubscriberMultiple()
        bus = InMemoryEventBus(subscribers=[subscriber1, subscriber2])

        event = SampleEvent1()  # type: ignore[call-arg]
        await bus.publish([event])

        assert len(subscriber1.handled_events) == 1
        assert subscriber1.handled_events[0] == event
        assert len(subscriber2.handled_events) == 1
        assert subscriber2.handled_events[0] == event

    @pytest.mark.asyncio
    async def test_publish_multiple_events_multiple_subscribers(self):
        """Test publishing multiple events to multiple subscribers."""
        subscriber1 = SampleSubscriber1()
        subscriber2 = SampleSubscriber2()
        subscriber_multiple = SampleSubscriberMultiple()
        bus = InMemoryEventBus(subscribers=[subscriber1, subscriber2, subscriber_multiple])

        event1 = SampleEvent1()  # type: ignore[call-arg]
        event2 = SampleEvent2()  # type: ignore[call-arg]
        await bus.publish([event1, event2])

        # Subscriber1 should only handle SampleEvent1
        assert len(subscriber1.handled_events) == 1
        assert subscriber1.handled_events[0] == event1

        # Subscriber2 should only handle SampleEvent2
        assert len(subscriber2.handled_events) == 1
        assert subscriber2.handled_events[0] == event2

        # SubscriberMultiple should handle both events
        assert len(subscriber_multiple.handled_events) == 2
        assert event1 in subscriber_multiple.handled_events
        assert event2 in subscriber_multiple.handled_events

    @pytest.mark.asyncio
    async def test_publish_event_not_subscribed(self):
        """Test publishing an event that no subscriber is subscribed to."""
        subscriber = SampleSubscriber1()
        bus = InMemoryEventBus(subscribers=[subscriber])

        event = SampleEvent2()  # type: ignore[call-arg]  # Subscriber is not subscribed to SampleEvent2
        await bus.publish([event])

        # Subscriber should not have handled the event
        assert len(subscriber.handled_events) == 0

    @pytest.mark.asyncio
    async def test_publish_empty_list(self):
        """Test publishing an empty list of events."""
        subscriber = SampleSubscriber1()
        bus = InMemoryEventBus(subscribers=[subscriber])

        await bus.publish([])

        assert len(subscriber.handled_events) == 0

    @pytest.mark.asyncio
    async def test_publish_subscriber_raises_exception(self):
        """Test that exceptions in subscribers don't break the event bus."""
        subscriber = SampleSubscriber1()

        async def failing_handler(event: SampleEvent1) -> None:  # noqa: ARG001
            raise ValueError("Test error")  # noqa: TRY003

        subscriber.on = failing_handler  # type: ignore[assignment]
        bus = InMemoryEventBus(subscribers=[subscriber])

        event = SampleEvent1()  # type: ignore[call-arg]

        # Exception should be raised
        with pytest.raises(ValueError, match="Test error"):
            await bus.publish([event])

    @pytest.mark.asyncio
    async def test_publish_multiple_subscribers_one_fails(self):
        """Test publishing when one subscriber fails but others succeed."""
        subscriber1 = SampleSubscriber1()
        subscriber2 = SampleSubscriber1()  # Second subscriber for same event

        async def failing_handler(event: SampleEvent1) -> None:  # noqa: ARG001
            raise ValueError("Test error")  # noqa: TRY003

        subscriber1.on = failing_handler  # type: ignore[assignment]
        bus = InMemoryEventBus(subscribers=[subscriber1, subscriber2])

        event = SampleEvent1()  # type: ignore[call-arg]

        # Exception should be raised, but both handlers should be called
        with pytest.raises(ValueError, match="Test error"):
            await bus.publish([event])

        # subscriber2 should have been called (gather runs all)
        assert len(subscriber2.handled_events) == 1

    @pytest.mark.asyncio
    async def test_register_subscribers_after_initialization(self):
        """Test that subscribers can be registered after initialization."""
        bus = InMemoryEventBus()
        assert bus._subscriptions == {}

        subscriber = SampleSubscriber1()
        bus._register_subscribers([subscriber])

        assert SampleEvent1 in bus._subscriptions
        assert len(bus._subscriptions[SampleEvent1]) == 1

    @pytest.mark.asyncio
    async def test_publish_with_same_event_type_twice(self):
        """Test publishing the same event type multiple times."""
        subscriber = SampleSubscriber1()
        bus = InMemoryEventBus(subscribers=[subscriber])

        event1 = SampleEvent1()  # type: ignore[call-arg]
        event2 = SampleEvent1()  # type: ignore[call-arg]
        await bus.publish([event1, event2])

        assert len(subscriber.handled_events) == 2
        assert event1 in subscriber.handled_events
        assert event2 in subscriber.handled_events
