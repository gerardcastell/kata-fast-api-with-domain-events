#!/usr/bin/env python3
"""
SQS Task Dispatcher Test Script.

This script demonstrates how to dispatch tasks to SQS for processing.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.config.settings import settings
from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.dispatcher import TaskDispatcher
from app.shared.infrastructure.sqs.models import TaskPriority


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


async def dispatch_sample_tasks():
    """Dispatch sample tasks to SQS."""
    logger = logging.getLogger(__name__)

    # Create SQS client and dispatcher
    sqs_client = SQSClient()
    dispatcher = TaskDispatcher(sqs_client)

    logger.info("Dispatching sample tasks...")

    # Task 1: Data Processing
    task_id_1 = await dispatcher.dispatch_task(
        task_type="data_processing",
        payload={
            "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "processing_type": "aggregation",
        },
        priority=TaskPriority.NORMAL,
    )
    logger.info(f"Dispatched data processing task: {task_id_1}")

    # Task 2: Email Notification
    task_id_2 = await dispatcher.dispatch_task(
        task_type="email_notification",
        payload={
            "recipient": "user@example.com",
            "subject": "Welcome to our service!",
            "body": "Thank you for signing up.",
            "template": "welcome",
        },
        priority=TaskPriority.HIGH,
    )
    logger.info(f"Dispatched email notification task: {task_id_2}")

    # Task 3: Report Generation
    task_id_3 = await dispatcher.dispatch_task(
        task_type="report_generation",
        payload={
            "report_type": "monthly_summary",
            "date_range": {
                "start": "2024-01-01",
                "end": "2024-01-31",
            },
            "format": "pdf",
        },
        priority=TaskPriority.LOW,
        delay_seconds=10,  # Process after 10 seconds
    )
    logger.info(f"Dispatched report generation task: {task_id_3}")

    # Batch tasks
    batch_tasks = [
        ("data_processing", {"data": [100, 200, 300], "processing_type": "transformation"}),
        ("email_notification", {"recipient": "admin@example.com", "subject": "System Alert"}),
        ("report_generation", {"report_type": "daily", "format": "csv"}),
    ]

    batch_task_ids = await dispatcher.dispatch_batch_tasks(
        tasks=batch_tasks,
        priority=TaskPriority.NORMAL,
    )
    logger.info(f"Dispatched batch tasks: {batch_task_ids}")

    logger.info("All tasks dispatched successfully!")


async def main():
    """Main function."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("SQS Task Dispatcher Test")

    # Validate configuration
    if not settings.sqs_queue_url:
        logger.error("SQS_QUEUE_URL is required")
        sys.exit(1)

    try:
        await dispatch_sample_tasks()
    except Exception:
        logger.exception("Error dispatching tasks")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDispatcher stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
