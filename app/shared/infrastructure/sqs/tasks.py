import asyncio
import logging
import random
from datetime import datetime, timezone

from app.shared.infrastructure.sqs.models import TaskMessage, TaskResult, TaskStatus
from app.shared.infrastructure.sqs.worker import TaskProcessor

logger = logging.getLogger(__name__)


class EmailServiceError(Exception):
    """Email service specific error for simulated failures and real errors."""


class DataProcessingTask(TaskProcessor):
    """Example long-running task for data processing."""

    def __init__(self):
        super().__init__("data_processing")

    async def process(self, message: TaskMessage) -> TaskResult:
        """Process data processing task."""
        try:
            # Extract task data
            data = message.payload.get("data", [])
            processing_type = message.payload.get("processing_type", "default")

            logger.info(f"Starting data processing task {message.task_id} with {len(data)} items")

            # Simulate long-running processing
            result = await self._process_data(data, processing_type)

            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.COMPLETED,
                result={
                    "processed_items": len(data),
                    "processing_type": processing_type,
                    "result": result,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                },
                completed_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            logger.exception(f"Error processing data task {message.task_id}")
            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.now(timezone.utc),
            )

    async def _process_data(self, data: list, processing_type: str) -> dict:
        """Simulate data processing."""
        # Simulate processing time (1-10 seconds)
        processing_time = random.uniform(1, 10)  # nosec B311
        await asyncio.sleep(processing_time)

        # Simulate different processing types
        if processing_type == "aggregation":
            result = {
                "total": sum(data) if all(isinstance(x, (int, float)) for x in data) else len(data),
                "count": len(data),
                "average": sum(data) / len(data)
                if data and all(isinstance(x, (int, float)) for x in data)
                else 0,
            }
        elif processing_type == "transformation":
            result = {
                "transformed": [str(item).upper() for item in data],
                "original_count": len(data),
            }
        else:
            result = {
                "processed": True,
                "items": data,
                "processing_time": processing_time,
            }

        return result


class EmailNotificationTask(TaskProcessor):
    """Example task for sending email notifications."""

    def __init__(self):
        super().__init__("email_notification")

    async def process(self, message: TaskMessage) -> TaskResult:
        """Process email notification task."""
        try:
            # Extract task data
            recipient = message.payload.get("recipient")
            subject = message.payload.get("subject", "Notification")
            template = message.payload.get("template")

            if not recipient:
                raise ValueError("Recipient email is required")  # noqa: TRY003, TRY301

            logger.info(f"Sending email to {recipient}: {subject}")

            # Simulate email sending (2-5 seconds)
            await asyncio.sleep(random.uniform(2, 5))  # nosec B311

            # Simulate occasional failures for testing retry logic
            if random.random() < 0.1:  # 10% failure rate  # nosec B311
                raise Exception("Simulated email service failure")  # noqa: TRY002, TRY003, TRY301

            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.COMPLETED,
                result={
                    "recipient": recipient,
                    "subject": subject,
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                    "template_used": template,
                },
                completed_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            logger.exception(f"Error sending email {message.task_id}")
            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.now(timezone.utc),
            )


class ReportGenerationTask(TaskProcessor):
    """Example task for generating reports."""

    def __init__(self):
        super().__init__("report_generation")

    async def process(self, message: TaskMessage) -> TaskResult:
        """Process report generation task."""
        try:
            # Extract task data
            report_type = message.payload.get("report_type", "summary")
            date_range = message.payload.get("date_range", {})
            format_type = message.payload.get("format", "pdf")

            logger.info(f"Generating {report_type} report in {format_type} format")

            # Simulate report generation (5-15 seconds)
            processing_time = random.uniform(5, 15)  # nosec B311
            await asyncio.sleep(processing_time)

            # Generate mock report data
            report_data = {
                "report_id": f"RPT-{message.task_id}",
                "type": report_type,
                "format": format_type,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "date_range": date_range,
                "pages": random.randint(1, 50),  # nosec B311
                "file_size_mb": round(random.uniform(0.5, 10.0), 2),  # nosec B311
            }

            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.COMPLETED,
                result=report_data,
                completed_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            logger.exception(f"Error generating report {message.task_id}")
            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.FAILED,
                error_message=str(e),
                completed_at=datetime.now(timezone.utc),
            )
