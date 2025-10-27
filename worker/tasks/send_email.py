# worker/handler.py
import asyncio


async def send_email(message: dict):
    """
    Implementa la lógica real de la tarea.
    Lanza excepción si algo falla para probar DLQ.
    """
    task = message.get("task")
    customer_id = message.get("customer_id")
    payload = message.get("payload", {})
    fail = message.get("fail", False)
    # Simula trabajo async
    await asyncio.sleep(15)

    # Simula fallo aleatorio para PoC
    if fail:
        error_message = f"Simulated failure on task send_email for customer {customer_id}"
        raise RuntimeError(error_message)

    # Aquí iría la lógica real (p. ej. enviar email)
    print(f"[handler] processed task={task} customer_id={customer_id} payload={payload}")
    return {"ok": True}
