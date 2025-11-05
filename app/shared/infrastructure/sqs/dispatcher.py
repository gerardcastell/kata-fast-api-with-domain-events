import logging
from typing import Any

from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.models import TaskMessage, TaskPriority

logger = logging.getLogger(__name__)


class TaskDispatcher:
    """Service for dispatching tasks to SQS."""

    def __init__(self, sqs_client: SQSClient):
        self.sqs_client = sqs_client

    async def dispatch_task(
        self,
        task_type: str,
        payload: dict[str, Any],
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
    ) -> str | None:
        """
        Dispatch a task to SQS queue.

        Args:
            task_type: Type of task to execute
            payload: Task data
            priority: Task priority
            delay_seconds: Delay before processing

        Returns:
            Task ID if successful, None otherwise
        """
        try:
            message = TaskMessage(
                task_type=task_type,
                payload=payload,
                priority=priority,
                delay_seconds=delay_seconds,
            )

            success = await self.sqs_client.send_message(message)

            if success:
                logger.info(f"Task dispatched successfully: {message.task_id}")
                return str(message.task_id)
            else:
                logger.error(f"Failed to dispatch task: {task_type}")
                return None

        except Exception:
            logger.exception("Error dispatching task")
            return None

    async def dispatch_batch_tasks(
        self,
        tasks: list[tuple[str, dict[str, Any]]],
        priority: TaskPriority = TaskPriority.NORMAL,
        delay_seconds: int = 0,
    ) -> list[str]:
        """
        Dispatch multiple tasks to SQS queue.

        Args:
            tasks: List of (task_type, payload) tuples
            priority: Task priority
            delay_seconds: Delay before processing

        Returns:
            List of task IDs that were successfully dispatched
        """
        dispatched_tasks = []

        for task_type, payload in tasks:
            task_id = await self.dispatch_task(
                task_type=task_type,
                payload=payload,
                priority=priority,
                delay_seconds=delay_seconds,
            )

            if task_id:
                dispatched_tasks.append(task_id)

        logger.info(f"Dispatched {len(dispatched_tasks)}/{len(tasks)} tasks")
        return dispatched_tasks
