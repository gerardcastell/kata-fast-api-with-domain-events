from abc import ABC, abstractmethod

from app.shared.infrastructure.sqs.models import TaskMessage


class SQSClientInterface(ABC):
    """Abstract interface for SQS operations."""

    @abstractmethod
    async def send_message(self, message: TaskMessage) -> bool:
        """Send a task message to SQS queue."""

    @abstractmethod
    async def receive_messages(self, max_messages: int = 10) -> list[TaskMessage]:
        """Receive task messages from SQS queue."""

    @abstractmethod
    async def delete_message(self, receipt_handle: str) -> bool:
        """Delete a message from SQS queue."""

    @abstractmethod
    async def change_message_visibility(self, receipt_handle: str, visibility_timeout: int) -> bool:
        """Change message visibility timeout."""

    @abstractmethod
    async def get_queue_attributes(self) -> dict:
        """Get queue attributes."""
