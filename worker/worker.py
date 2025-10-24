# worker/worker.py
import asyncio
import contextlib
import json
import logging
import os

from aio_pika import connect_robust, ExchangeType
from aio_pika.abc import AbstractIncomingMessage

from worker.tasks.send_email import send_email

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

# ============================================================
# TASK REGISTRY - Configure your consumers/handlers here
# ============================================================
TASK_HANDLERS = {
    "send_email": send_email,
    # Add more task handlers here:
    # "send_sms": send_sms,  # noqa: ERA001
    # "process_payment": process_payment,  # noqa: ERA001
    # "generate_report": generate_report,  # noqa: ERA001
}
# ============================================================


async def setup_queues(channel):
    # 1) Declare DLX exchange and DLQ
    dlx = await channel.declare_exchange("tasks.dlx", ExchangeType.DIRECT, durable=True)
    dlq = await channel.declare_queue("tasks.dlq", durable=True)
    await dlq.bind(dlx, routing_key="tasks.main")

    # 2) Declare main exchange + main queue with DLX arg
    exchange = await channel.declare_exchange("tasks", ExchangeType.DIRECT, durable=True)

    queue_args = {
        "x-dead-letter-exchange": "tasks.dlx",  # messages rejected go to tasks.dlx
    }
    main_queue = await channel.declare_queue("tasks.main", durable=True, arguments=queue_args)
    await main_queue.bind(exchange, routing_key="tasks.main")

    return main_queue


async def on_message(message: AbstractIncomingMessage):
    async with message.process(
        ignore_processed=True
    ):  # context ensures no double processing for some cases
        try:
            body = message.body.decode()
            data = json.loads(body)
            task_name = data.get("task")

            logger.info(f"Received message: {data}")

            # Route to the appropriate handler
            handler = TASK_HANDLERS.get(task_name)
            if handler is None:
                logger.error(
                    f"Unknown task type: {task_name}. Available tasks: {list(TASK_HANDLERS.keys())}"
                )
                await message.reject(requeue=False)
                return

            # Process task with the appropriate handler
            await handler(data)

            # manual ack
            await message.ack()
            logger.info(f"Message ACKed for task: {task_name}")
        except Exception:
            logger.exception("Handler failed, rejecting message to DLQ")
            # reject without requeue => goes to DLX/DLQ
            try:
                await message.reject(requeue=False)
            except Exception:
                logger.exception("Failed to reject message")


async def main():
    connection = await connect_robust(RABBIT_URL)
    async with connection:
        channel = await connection.channel()
        # control prefetch (QoS) - prefetch_count=1 means process one message at a time
        await channel.set_qos(prefetch_count=1)

        main_queue = await setup_queues(channel)

        logger.info("Starting consumer, waiting for messages...")
        await main_queue.consume(on_message, no_ack=False)

        # keep running
        with contextlib.suppress(asyncio.CancelledError):
            await asyncio.Future()  # run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped")
