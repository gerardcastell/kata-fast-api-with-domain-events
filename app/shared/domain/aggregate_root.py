from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.shared.domain.event.domain_event import DomainEvent


class AggregateRoot(BaseModel):
    model_config = ConfigDict(frozen=True)

    domain_events: Annotated[
        list[DomainEvent], Field(description="The events that have occurred on the aggregate")
    ]

    def pull_domain_events(self) -> list[DomainEvent]:
        events = self.domain_events
        self.domain_events = []
        return events

    def record_domain_event(self, event: DomainEvent):
        self.domain_events.append(event)
