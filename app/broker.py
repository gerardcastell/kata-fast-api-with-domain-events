# app/broker.py
import json
import os

import aio_pika
from aio_pika import ExchangeType

RABBIT_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


async def get_connection():
    return await aio_pika.connect_robust(RABBIT_URL)


async def publish_task(message_body: dict, routing_key: str = "tasks.main"):
    """∫
    Publica un mensaje JSON en exchange 'tasks' con routing_key por defecto 'tasks.main'
    """
    connection = await get_connection()
    async with connection:
        channel = await connection.channel()
        # durable exchange
        exchange = await channel.declare_exchange("tasks", ExchangeType.DIRECT, durable=True)
        payload = json.dumps(message_body).encode()
        await exchange.publish(
            aio_pika.Message(
                body=payload,
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )
