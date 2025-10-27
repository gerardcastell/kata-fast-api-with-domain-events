# app/broker.py
import json
import os

import aio_pika
from aio_pika import ExchangeType

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


async def get_connection():
    return await aio_pika.connect_robust(RABBIT_URL)


async def publish_task(
    message_body: dict, routing_key: str = "tasks.main", exchange_name: str = "tasks"
):
    """
    Publish a JSON message to a RabbitMQ exchange

    Args:
        message_body: The message payload as a dictionary
        routing_key: The routing key to use (determines which queue receives the message)
        exchange_name: The exchange to publish to (default: "tasks")

    Example:
        # Publish to main queue
        await publish_task({"task": "send_email", "customer_id": 123}, routing_key="tasks.main")

        # Publish to notifications queue
        await publish_task({"task": "send_sms", "phone": "+123"}, routing_key="notifications")

        # Publish to reports queue
        await publish_task({"task": "generate_report", "type": "sales"}, routing_key="reports")
    """
    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        # durable exchange
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT, durable=True)
        payload = json.dumps(message_body).encode()
        await exchange.publish(
            aio_pika.Message(
                body=payload,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
