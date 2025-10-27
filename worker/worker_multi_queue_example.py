# worker/worker_multi_queue_example.py
"""
Example configuration showing how to use multiple queues.

To use this configuration:
1. Copy the QUEUE_CONFIGS section to worker/worker.py
2. Make sure all task handlers are imported
3. Restart the worker

This example shows three different queues:
- Notifications queue: High concurrency for quick tasks
- Reports queue: Low concurrency for heavy tasks
- Main queue: Default queue for general tasks
"""

from worker.tasks.generate_report import generate_report
from worker.tasks.send_email import send_email
from worker.tasks.send_sms import send_sms
from worker.worker import QueueConfig

# Example multi-queue configuration
QUEUE_CONFIGS_EXAMPLE: list[QueueConfig] = [
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
        prefetch_count=1,  # Process up to 10 notifications concurrently
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
        prefetch_count=1,
    ),
]


# Example: How to publish to different queues
"""
from app.broker import publish_task

# Send notification
await publish_task(
    message_body={
        "task": "send_email",
        "customer_id": 123,
        "payload": {
            "to": "user@example.com",
            "subject": "Welcome!",
            "body": "Thanks for signing up"
        }
    },
    routing_key="notifications"  # Routes to notifications.queue
)

# Generate report
await publish_task(
    message_body={
        "task": "generate_report",
        "payload": {
            "report_type": "sales",
            "date_range": "2024-01"
        }
    },
    routing_key="reports"  # Routes to reports.queue
)

# General task
await publish_task(
    message_body={
        "task": "some_task",
        "payload": {...}
    },
    routing_key="tasks.main"  # Routes to tasks.main
)
"""
