# worker/tasks/generate_report.py
import asyncio
import logging

logger = logging.getLogger("worker.tasks.generate_report")


async def generate_report(message: dict):
    """
    Generate a heavy report - should run in a low-concurrency queue
    """
    payload = message.get("payload", {})
    report_type = payload.get("report_type")
    date_range = payload.get("date_range")
    fail = message.get("fail", False)
    # Simula trabajo async
    await asyncio.sleep(15)
    if fail:
        error_message = "Simulated failure on task generate_report"
        raise RuntimeError(error_message)
    logger.info(f"Generating {report_type} report for {date_range}")

    # Here you would generate the actual report
    logger.info(f"Report generated successfully: {report_type}")

    return {"ok": True, "report_url": f"/reports/{report_type}_123.pdf"}
