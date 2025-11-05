import uuid
from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DomainEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_id: Annotated[
        str,
        Field(
            description="The unique identifier for the event",
            default_factory=lambda: str(uuid.uuid4()),
        ),
    ]
    occurred_at: Annotated[
        datetime,
        Field(
            description="The date and time the event occurred",
            default_factory=lambda: datetime.now(timezone.utc),
        ),
    ]
    aggregate_id: Annotated[
        str,
        Field(
            description="The unique identifier for the aggregate",
            default_factory=lambda: str(uuid.uuid4()),
        ),
    ]
