#!/usr/bin/env python3
"""
SQS Worker CLI script.

This script starts the SQS worker to process async tasks.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from app.config.settings import settings
from app.shared.containers.main import Container
from app.shared.infrastructure.sqs import tasks as tasks_module
from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.models import WorkerConfig
from app.shared.infrastructure.sqs.tasks import (
    create_customer_creation_task,
    DataProcessingTask,
    EmailNotificationTask,
    ReportGenerationTask,
)
from app.shared.infrastructure.sqs.worker import SQSWorker


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("worker.log"),
        ],
    )


async def main():
    """Main worker function."""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Starting SQS Worker...")

    # Validate configuration
    if not settings.sqs_queue_url:
        logger.error("SQS_QUEUE_URL is required")
        sys.exit(1)

    # Create SQS client
    sqs_client = SQSClient()

    # Create worker configuration
    worker_config = WorkerConfig(
        max_concurrent_tasks=5,
        poll_interval_seconds=1,
        shutdown_timeout_seconds=30,
        health_check_interval_seconds=60,
    )

    # Create worker
    worker = SQSWorker(sqs_client, worker_config)

    # Create dependency injection container
    container = Container()
    container.config.from_pydantic(settings)
    container.wire(modules=[tasks_module])

    # Register task processors
    worker.register_processor(DataProcessingTask())
    worker.register_processor(EmailNotificationTask())
    worker.register_processor(ReportGenerationTask())

    # Register customer creation task with dependency injection
    customer_creation_task = create_customer_creation_task()

    worker.register_processor(customer_creation_task)

    logger.info("Worker configured with processors:")
    logger.info("- data_processing")
    logger.info("- email_notification")
    logger.info("- report_generation")
    logger.info("- customer_creation")

    try:
        # Start the worker
        await worker.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception:
        logger.exception("Worker error")
    finally:
        await worker.stop()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWorker stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
