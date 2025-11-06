from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_serializer


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    """Task priority enumeration."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TaskMessage(BaseModel):
    """SQS message model for task processing."""

    task_id: UUID = Field(default_factory=uuid4)
    task_type: str = Field(..., description="Type of task to execute")
    payload: dict[str, Any] = Field(default_factory=dict, description="Task data")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    delay_seconds: int = Field(default=0, description="Delay before processing")
    receipt_handle: str | None = Field(default=None, description="SQS receipt handle")
    approximate_receive_count: int | None = Field(
        default=None, description="SQS approximate receive count"
    )

    @field_serializer("task_id")
    def serialize_task_id(self, value: UUID) -> str:
        """Serialize UUID to string."""
        return str(value)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        """Serialize datetime to ISO format."""
        return value.isoformat()


class TaskResult(BaseModel):
    """Task execution result model."""

    task_id: UUID
    status: TaskStatus
    result: dict[str, Any] | None = None
    error_message: str | None = None
    completed_at: datetime | None = None
    processing_time_seconds: float | None = None

    @field_serializer("task_id")
    def serialize_task_id(self, value: UUID) -> str:
        """Serialize UUID to string."""
        return str(value)

    @field_serializer("completed_at")
    def serialize_completed_at(self, value: datetime | None) -> str | None:
        """Serialize datetime to ISO format."""
        return value.isoformat() if value is not None else None


class WorkerConfig(BaseModel):
    """Worker configuration model."""

    max_concurrent_tasks: int = Field(default=5)
    poll_interval_seconds: int = Field(default=1)
    shutdown_timeout_seconds: int = Field(default=30)
    health_check_interval_seconds: int = Field(default=60)
