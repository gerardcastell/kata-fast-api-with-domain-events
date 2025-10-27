# worker/worker.py
import asyncio
import contextlib
import json
import logging
import os
from collections.abc import Callable
from dataclasses import dataclass

from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue

from worker.tasks.generate_report import generate_report
from worker.tasks.send_email import send_email
from worker.tasks.send_sms import send_sms

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")


# ============================================================
# QUEUE CONFIGURATION
# ============================================================
@dataclass
class QueueConfig:
    """Configuration for a single queue"""

    name: str
    routing_key: str
    task_handlers: dict[str, Callable]
    prefetch_count: int = 1
    exchange_name: str = "tasks"
    dlx_exchange_name: str = "tasks.dlx"
    dlq_name: str = "tasks.dlq"


# ============================================================
# TASK REGISTRY - Configure your queues and handlers here
# ============================================================
QUEUE_CONFIGS: list[QueueConfig] = [
    # Notifications Queue - High Throughput
    # Use for: Emails, SMS, Push notifications
    # Characteristics: Fast, lightweight, high concurrency
    QueueConfig(
        name="notifications.queue",
        routing_key="notifications",
        task_handlers={
            "send_email": send_email,
            "send_sms": send_sms,
            # Add more notification handlers here
        },
        prefetch_count=10,  # Process up to 10 notifications concurrently
        dlx_exchange_name="notifications.dlx",
        dlq_name="notifications.dlq",
    ),
    # Reports Queue - Heavy Processing
    # Use for: Report generation, data exports, analytics
    # Characteristics: Slow, resource-intensive, low concurrency
    QueueConfig(
        name="reports.queue",
        routing_key="reports",
        task_handlers={
            "generate_report": generate_report,
            # Add more report handlers here
        },
        prefetch_count=1,  # Process one report at a time
    ),
    # Main Queue - General Purpose
    # Use for: Default tasks, miscellaneous operations
    # Characteristics: Moderate load, standard processing
    QueueConfig(
        name="tasks.main",
        routing_key="tasks.main",
        task_handlers={
            # Add general task handlers here
        },
        prefetch_count=5,
    ),
]
# ============================================================


async def setup_queue(channel, config: QueueConfig) -> AbstractQueue:
    """
    Set up a single queue with its DLX/DLQ configuration
    """
    # 1) Declare DLX exchange and DLQ
    dlx = await channel.declare_exchange(
        config.dlx_exchange_name, ExchangeType.DIRECT, durable=True
    )
    dlq = await channel.declare_queue(config.dlq_name, durable=True)
    await dlq.bind(dlx, routing_key=config.routing_key)

    # 2) Declare main exchange + queue with DLX arg
    exchange = await channel.declare_exchange(
        config.exchange_name, ExchangeType.DIRECT, durable=True
    )

    queue_args = {
        "x-dead-letter-exchange": config.dlx_exchange_name,
    }
    queue = await channel.declare_queue(config.name, durable=True, arguments=queue_args)
    await queue.bind(exchange, routing_key=config.routing_key)

    logger.info(
        f"Queue '{config.name}' configured with routing_key='{config.routing_key}', "
        f"prefetch={config.prefetch_count}, handlers={list(config.task_handlers.keys())}"
    )
    return queue


def create_message_handler(config: QueueConfig):
    """
    Factory function to create a message handler for a specific queue configuration
    """

    async def on_message(message: AbstractIncomingMessage):
        async with message.process(ignore_processed=True):
            try:
                body = message.body.decode()
                data = json.loads(body)
                task_name = data.get("task")

                logger.info(f"[{config.name}] Received message: {data}")

                # Route to the appropriate handler
                handler = config.task_handlers.get(task_name)
                if handler is None:
                    logger.error(
                        f"[{config.name}] Unknown task type: {task_name}. "
                        f"Available tasks: {list(config.task_handlers.keys())}"
                    )
                    await message.reject(requeue=False)
                    return

                # Process task with the appropriate handler
                await handler(data)

                # manual ack
                await message.ack()
                logger.info(f"[{config.name}] Message ACKed for task: {task_name}")
            except Exception:
                logger.exception(f"[{config.name}] Handler failed, rejecting message to DLQ")
                try:
                    await message.reject(requeue=False)
                except Exception:
                    logger.exception(f"[{config.name}] Failed to reject message")

    return on_message


async def main():
    connection = await connect_robust(RABBIT_URL)
    async with connection:
        # Set up all queues and start consuming
        consumers = []

        for config in QUEUE_CONFIGS:
            # Create a separate channel for each queue for better isolation
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=config.prefetch_count)

            # Setup queue infrastructure
            queue = await setup_queue(channel, config)

            # Create and register consumer
            handler = create_message_handler(config)
            await queue.consume(handler, no_ack=False)
            consumers.append((config.name, queue))

        logger.info(f"Worker started, consuming from {len(consumers)} queue(s)")
        for queue_name, _ in consumers:
            logger.info(f"  - {queue_name}")

        # keep running
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped")
