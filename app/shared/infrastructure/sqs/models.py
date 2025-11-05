from datetime import datetime
from enum import Enum
from typing import Any, ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


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
    _receipt_handle: str | None = Field(default=None, description="SQS receipt handle")
    _approximate_receive_count: int | None = Field(
        default=None, description="SQS approximate receive count"
    )

    class Config:
        json_encoders: ClassVar[dict] = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class TaskResult(BaseModel):
    """Task execution result model."""

    task_id: UUID
    status: TaskStatus
    result: dict[str, Any] | None = None
    error_message: str | None = None
    completed_at: datetime | None = None
    processing_time_seconds: float | None = None

    class Config:
        json_encoders: ClassVar[dict] = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }


class WorkerConfig(BaseModel):
    """Worker configuration model."""

    max_concurrent_tasks: int = Field(default=5)
    poll_interval_seconds: int = Field(default=1)
    shutdown_timeout_seconds: int = Field(default=30)
    health_check_interval_seconds: int = Field(default=60)
