# Multi-Queue Setup Guide

This guide explains how to work with multiple queues in the RabbitMQ worker system.

## Architecture Overview

The worker system now supports multiple queues with independent configurations. Each queue can have:

- **Different task handlers**: Route specific tasks to specific queues
- **Different prefetch counts**: Control concurrency per queue
- **Independent DLQ/DLX**: Each queue has its own dead-letter handling
- **Separate channels**: Better isolation between queues

## Configuration

Queues are configured in `worker/worker.py` using the `QueueConfig` dataclass:

```python
@dataclass
class QueueConfig:
    name: str                     # Queue name
    routing_key: str              # Routing key for binding
    task_handlers: Dict[str, Callable]  # Task name -> handler function
    prefetch_count: int = 1       # QoS prefetch (concurrency control)
    exchange_name: str = "tasks"  # Exchange to use
    dlx_exchange_name: str = "tasks.dlx"  # Dead-letter exchange
    dlq_name: str = "tasks.dlq"   # Dead-letter queue
```

## Adding New Queues

### 1. Create Task Handlers

Create a new file in `worker/tasks/`:

```python
# worker/tasks/my_task.py
import asyncio
import logging

logger = logging.getLogger("worker.tasks.my_task")

async def my_task_handler(message: dict):
    """Handle my custom task"""
    payload = message.get("payload", {})
    
    # Your business logic here
    await asyncio.sleep(1)
    
    logger.info(f"Task completed: {payload}")
    return {"ok": True}
```

### 2. Register the Queue

Add a new `QueueConfig` to the `QUEUE_CONFIGS` list in `worker/worker.py`:

```python
from worker.tasks.my_task import my_task_handler

QUEUE_CONFIGS: List[QueueConfig] = [
    # Existing queues...
    
    # Your new queue
    QueueConfig(
        name="my_queue",
        routing_key="my_routing_key",
        task_handlers={
            "my_task": my_task_handler,
        },
        prefetch_count=5,  # Process up to 5 messages concurrently
    ),
]
```

### 3. Publish to Your Queue

Use the `publish_task` function with the appropriate routing key:

```python
from app.broker import publish_task

# Publish to your new queue
await publish_task(
    message_body={
        "task": "my_task",
        "customer_id": 123,
        "payload": {"data": "value"}
    },
    routing_key="my_routing_key"
)
```

## Common Queue Patterns

### Pattern 1: By Task Type

Separate queues for different types of operations:

```python
QUEUE_CONFIGS = [
    QueueConfig(
        name="notifications.queue",
        routing_key="notifications",
        task_handlers={
            "send_email": send_email,
            "send_sms": send_sms,
            "send_push": send_push_notification,
        },
        prefetch_count=10,  # High concurrency for quick tasks
    ),
    QueueConfig(
        name="reports.queue",
        routing_key="reports",
        task_handlers={
            "generate_report": generate_report,
            "export_data": export_data,
        },
        prefetch_count=1,  # Low concurrency for heavy tasks
    ),
]
```

### Pattern 2: By Priority

Separate queues for different priority levels:

```python
QUEUE_CONFIGS = [
    QueueConfig(
        name="high_priority.queue",
        routing_key="priority.high",
        task_handlers={
            "send_email": send_email,
            "process_payment": process_payment,
        },
        prefetch_count=20,
    ),
    QueueConfig(
        name="low_priority.queue",
        routing_key="priority.low",
        task_handlers={
            "cleanup_old_data": cleanup_old_data,
            "generate_analytics": generate_analytics,
        },
        prefetch_count=2,
    ),
]
```

### Pattern 3: By Domain/Context

Separate queues for different bounded contexts:

```python
QUEUE_CONFIGS = [
    QueueConfig(
        name="customers.queue",
        routing_key="domain.customers",
        task_handlers={
            "customer_created": handle_customer_created,
            "customer_updated": handle_customer_updated,
        },
        prefetch_count=5,
    ),
    QueueConfig(
        name="orders.queue",
        routing_key="domain.orders",
        task_handlers={
            "order_placed": handle_order_placed,
            "order_shipped": handle_order_shipped,
        },
        prefetch_count=10,
    ),
]
```

## Publishing Messages

### Basic Publishing

```python
from app.broker import publish_task

# Publish to main queue
await publish_task(
    message_body={"task": "send_email", "customer_id": 123},
    routing_key="tasks.main"
)
```

### Publishing to Different Queues

```python
# Publish to notifications queue
await publish_task(
    message_body={
        "task": "send_sms",
        "customer_id": 123,
        "payload": {"phone": "+1234567890", "text": "Hello!"}
    },
    routing_key="notifications"
)

# Publish to reports queue
await publish_task(
    message_body={
        "task": "generate_report",
        "payload": {"report_type": "sales", "date_range": "2024-01"}
    },
    routing_key="reports"
)
```

## Concurrency Control

The `prefetch_count` parameter controls how many messages a queue will process concurrently:

- **prefetch_count=1**: Process one message at a time (serial processing)
  - Good for: Heavy tasks, tasks requiring exclusive resources
  - Example: Report generation, database migrations

- **prefetch_count=5-10**: Moderate concurrency
  - Good for: Standard API calls, moderate workloads
  - Example: Sending emails, calling external APIs

- **prefetch_count=20+**: High concurrency
  - Good for: Lightweight tasks, high throughput requirements
  - Example: Simple notifications, logging tasks

## Dead Letter Queue (DLQ)

Each queue automatically has DLQ support:

1. When a task handler raises an exception, the message is rejected
2. Rejected messages are routed to the DLX (Dead Letter Exchange)
3. The DLX routes messages to the DLQ for later inspection

All queues share the same DLQ by default (`tasks.dlq`), but you can configure separate DLQs:

```python
QueueConfig(
    name="critical.queue",
    routing_key="critical",
    task_handlers={...},
    dlx_exchange_name="critical.dlx",
    dlq_name="critical.dlq",
)
```

## Monitoring

The worker logs detailed information about queue setup and message processing:

```
INFO:worker:Queue 'tasks.main' configured with routing_key='tasks.main', prefetch=1, handlers=['send_email']
INFO:worker:Queue 'notifications.queue' configured with routing_key='notifications', prefetch=10, handlers=['send_sms', 'send_push']
INFO:worker:Worker started, consuming from 2 queue(s)
INFO:worker:  - tasks.main
INFO:worker:  - notifications.queue
```

Each message includes the queue name in logs:

```
INFO:worker:[tasks.main] Received message: {...}
INFO:worker:[tasks.main] Message ACKed for task: send_email
```

## Testing

### Testing with curl

```bash
# Test main queue
curl -X POST http://localhost:8000/api/v1/customers/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "name": "Test User"}'

# The customer creation will publish to the queue
```

### Manual Publishing

You can manually publish messages for testing:

```python
import asyncio
from app.broker import publish_task

async def test_queue():
    await publish_task(
        message_body={
            "task": "send_email",
            "customer_id": 999,
            "payload": {"subject": "Test", "body": "Testing"}
        },
        routing_key="tasks.main"
    )

asyncio.run(test_queue())
```

## Best Practices

1. **Separate by Concerns**: Group related tasks into the same queue
2. **Control Concurrency**: Set appropriate prefetch_count based on task characteristics
3. **Monitor DLQs**: Regularly check DLQs for failed messages
4. **Idempotent Handlers**: Design handlers to be safely retryable
5. **Logging**: Include queue name and task details in logs
6. **Error Handling**: Let exceptions bubble up to trigger DLQ routing

## Troubleshooting

### Messages not being consumed

1. Check that the queue is declared in `QUEUE_CONFIGS`
2. Verify the routing key matches between publisher and queue configuration
3. Check worker logs for errors during setup

### Messages going to DLQ immediately

1. Check handler logs for exceptions
2. Verify the task name in the message matches a registered handler
3. Ensure handler is properly imported in worker.py

### Low throughput

1. Increase `prefetch_count` for the queue
2. Consider splitting heavy tasks into separate queues
3. Check if handlers are CPU or I/O bound and optimize accordingly

## Example: Complete Queue Addition

Here's a complete example of adding a new "analytics" queue:

```python
# 1. Create handler: worker/tasks/analytics.py
import asyncio
import logging

logger = logging.getLogger("worker.tasks.analytics")

async def track_event(message: dict):
    payload = message.get("payload", {})
    event = payload.get("event")
    user_id = payload.get("user_id")
    
    logger.info(f"Tracking event: {event} for user {user_id}")
    await asyncio.sleep(0.5)  # Simulate API call to analytics service
    
    return {"ok": True}

# 2. Update worker/worker.py
from worker.tasks.analytics import track_event

QUEUE_CONFIGS = [
    # ... existing queues ...
    QueueConfig(
        name="analytics.queue",
        routing_key="analytics",
        task_handlers={
            "track_event": track_event,
        },
        prefetch_count=20,  # High throughput for analytics
    ),
]

# 3. Publish from your app
from app.broker import publish_task

await publish_task(
    message_body={
        "task": "track_event",
        "payload": {
            "event": "user_login",
            "user_id": 123,
            "timestamp": "2024-01-15T10:30:00Z"
        }
    },
    routing_key="analytics"
)
```

## Migration from Single Queue

If you're migrating from the old single-queue setup:

1. **No Breaking Changes**: The default configuration maintains backward compatibility
2. **Gradual Migration**: Add new queues while keeping the main queue operational
3. **Update Publishers**: Gradually update `publish_task` calls to use specific routing keys
4. **Monitor**: Watch logs to ensure messages are routed correctly

Your existing code will continue to work with the default `tasks.main` queue!

