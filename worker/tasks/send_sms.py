# worker/tasks/send_sms.py
import asyncio
import logging

logger = logging.getLogger("worker.tasks.send_sms")


async def send_sms(message: dict):
    """
    Send an SMS notification to a customer
    """
    customer_id = message.get("customer_id")
    payload = message.get("payload", {})
    phone_number = payload.get("phone_number")
    text = payload.get("text")
    fail = message.get("fail", False)
    if fail:
        error_message = "Simulated failure on task send_sms"
        raise RuntimeError(error_message)
    logger.info(f"Sending SMS to {phone_number} for customer {customer_id}")

    # Simulate async work
    await asyncio.sleep(2)

    # Here you would integrate with an SMS provider (Twilio, etc.)
    logger.info(f"SMS sent successfully: {text[:50]}...")

    return {"ok": True, "message_id": "sms_123"}
