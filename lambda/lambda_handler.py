#!/usr/bin/env python3
# ruff: noqa: I001
"""
Lambda-style SQS message handler and local poller.

This module provides two execution modes:
- AWS Lambda handler: `handler(event, context)` processes SQS event records
- Script mode: `python lambda_handler.py` runs a poller loop (used by docker-compose)
"""

import asyncio
import json
import logging
import signal
import sys
from pathlib import Path
from typing import Any

# Ensure project root is on the path when executed as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config.settings import settings
from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.models import (
    TaskMessage,
    TaskResult,
    TaskStatus,
    WorkerConfig,
)
from app.shared.infrastructure.sqs.tasks import (
    DataProcessingTask,
    EmailNotificationTask,
    ReportGenerationTask,
)


logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("worker.log"),
        ],
    )


def _get_processors() -> dict[str, Any]:
    """Return available task processors keyed by task_type."""
    processors = [
        DataProcessingTask(),
        EmailNotificationTask(),
        ReportGenerationTask(),
    ]
    return {p.task_type: p for p in processors}


async def _process_task_message(
    sqs_client: SQSClient,
    processors: dict[str, Any],
    message: TaskMessage,
) -> None:
    """Process a single TaskMessage using registered processors and handle ACK/retry."""
    try:
        processor = processors.get(message.task_type)
        if not processor:
            logger.error("No processor found for task type: %s", message.task_type)
            await _handle_failure(sqs_client, message, "No processor found")
            return

        result: TaskResult = await processor.process(message)

        if result.status == TaskStatus.COMPLETED:
            await _handle_success(sqs_client, message, result)
        else:
            await _handle_failure(sqs_client, message, result.error_message or "Unknown error")

    except Exception as exc:
        logger.exception("Unhandled error processing task %s", message.task_id)
        await _handle_failure(sqs_client, message, str(exc))


async def _handle_success(sqs_client: SQSClient, message: TaskMessage, result: TaskResult) -> None:
    try:
        if hasattr(message, "_receipt_handle"):
            await sqs_client.delete_message(message._receipt_handle)  # type: ignore[arg-type]
        logger.info("Task %s completed successfully: %s", message.task_id, result)
    except Exception:
        logger.exception("Error acknowledging successful task %s", message.task_id)


async def _handle_failure(sqs_client: SQSClient, message: TaskMessage, error_message: str) -> None:
    try:
        if message.retry_count < message.max_retries:
            message.retry_count += 1
            # Exponential backoff capped at 15 minutes
            message.delay_seconds = min(60 * (2**message.retry_count), 900)
            await sqs_client.send_message(message)
            logger.info(
                "Task %s failed: %s. Retrying %d/%d",
                message.task_id,
                error_message,
                message.retry_count,
                message.max_retries,
            )
        else:
            if hasattr(message, "_receipt_handle"):
                await sqs_client.delete_message(message._receipt_handle)  # type: ignore[arg-type]
            logger.error(
                "Task %s failed permanently after %d retries: %s",
                message.task_id,
                message.max_retries,
                error_message,
            )
    except Exception:
        logger.exception("Error handling failure for task %s", message.task_id)


def handler(event: dict, _context: Any) -> dict:
    """
    AWS Lambda handler for SQS events.

    Expects `event` with Records list, each record having `body` containing a TaskMessage JSON.
    """
    setup_logging()
    logger.info("Lambda handler invoked with %d record(s)", len(event.get("Records", [])))

    async def _run() -> None:
        sqs_client = SQSClient()
        processors = _get_processors()

        # Process each SQS record
        for record in event.get("Records", []):
            try:
                body = record.get("body")
                if not body:
                    logger.warning("Record without body, skipping")
                    continue

                data = json.loads(body)
                task_message = TaskMessage(**data)
                # Inject receipt handle if present to allow deletion
                receipt_handle = record.get("receiptHandle")
                if receipt_handle:
                    task_message._receipt_handle = receipt_handle  # type: ignore[attr-defined]

                await _process_task_message(sqs_client, processors, task_message)
            except Exception:
                logger.exception("Error processing record")

    asyncio.run(_run())

    return {"statusCode": 200, "body": json.dumps({"processed": len(event.get("Records", []))})}


# Script mode: emulate SQS-triggered Lambda by polling
async def _poller() -> None:
    setup_logging()
    logger.info("Starting Lambda poller for SQS messages...")

    if not settings.sqs_queue_url:
        logger.error("SQS_QUEUE_URL is required")
        sys.exit(1)

    sqs_client = SQSClient()
    processors = _get_processors()
    config = WorkerConfig()

    stop_event = asyncio.Event()

    def _signal_handler(signum, _frame):
        logger.info("Received signal %s, shutting down poller...", signum)
        stop_event.set()

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    try:
        while not stop_event.is_set():
            messages = await sqs_client.receive_messages(max_messages=settings.sqs_max_messages)
            if not messages:
                await asyncio.sleep(config.poll_interval_seconds)
                continue

            # Process concurrently but modestly bounded by settings.sqs_max_messages
            await asyncio.gather(
                *[_process_task_message(sqs_client, processors, m) for m in messages],
                return_exceptions=True,
            )
    except Exception:
        logger.exception("Poller error")
    finally:
        logger.info("Lambda poller stopped")


if __name__ == "__main__":
    asyncio.run(_poller())
