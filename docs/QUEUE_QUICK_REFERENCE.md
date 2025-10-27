# Multi-Queue Quick Reference

Quick reference card for working with multiple queues in RabbitMQ.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Application                     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            app/broker.py                             │  │
│  │                                                       │  │
│  │  publish_task(message, routing_key="tasks.main")    │  │
│  └───────────────────────┬──────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       RabbitMQ Exchange                      │
│                      exchange: "tasks"                       │
│                                                              │
│  Routes messages based on routing_key                       │
└──────┬────────────────┬────────────────┬────────────────────┘
       │                │                │
       │ "tasks.main"   │ "notifications"│ "reports"
       │                │                │
       ▼                ▼                ▼
  ┌─────────┐     ┌─────────────┐  ┌───────────┐
  │tasks.   │     │notifications│  │reports.   │
  │main     │     │.queue       │  │queue      │
  └────┬────┘     └──────┬──────┘  └─────┬─────┘
       │                 │               │
       ▼                 ▼               ▼
┌─────────────────────────────────────────────────────────────┐
│                     Worker Process                           │
│                  worker/worker.py                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Channel 1    │  │ Channel 2    │  │ Channel 3    │     │
│  │ prefetch=1   │  │ prefetch=10  │  │ prefetch=1   │     │
│  │              │  │              │  │              │     │
│  │ send_email   │  │ send_sms     │  │ generate_    │     │
│  │              │  │ send_push    │  │ report       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Quick Commands

### Start Services

```bash
# Start RabbitMQ
docker-compose up -d rabbitmq

# Start Worker
python -m worker.worker

# Start FastAPI
fastapi dev app/main.py
```

### Test Publishing

```bash
# Test script
python scripts/test_multi_queue.py

# Manual test in Python
python -c "
import asyncio
from app.broker import publish_task

async def test():
    await publish_task(
        {'task': 'send_email', 'customer_id': 123},
        routing_key='tasks.main'
    )

asyncio.run(test())
"
```

## Configuration Cheat Sheet

### Add a New Queue

```python
# 1. Create handler: worker/tasks/my_task.py
async def my_task(message: dict):
    payload = message.get("payload", {})
    # Your logic here
    return {"ok": True}

# 2. Add to worker/worker.py
from worker.tasks.my_task import my_task

QUEUE_CONFIGS: list[QueueConfig] = [
    QueueConfig(
        name="my.queue",
        routing_key="my_key",
        task_handlers={"my_task": my_task},
        prefetch_count=5,
    ),
]

# 3. Publish messages
await publish_task(
    {"task": "my_task", "payload": {...}},
    routing_key="my_key"
)
```

## Common Patterns

### Pattern: Task Type Separation

```python
# Fast tasks (emails, notifications)
QueueConfig(
    name="fast.queue",
    routing_key="fast",
    task_handlers={"send_email": send_email, "send_sms": send_sms},
    prefetch_count=20,  # High concurrency
)

# Slow tasks (reports, exports)
QueueConfig(
    name="slow.queue",
    routing_key="slow",
    task_handlers={"generate_report": generate_report},
    prefetch_count=1,  # Serial processing
)
```

### Pattern: Priority Levels

```python
# High priority
QueueConfig(name="priority.high", routing_key="priority.high", ..., prefetch_count=20)

# Normal priority
QueueConfig(name="priority.normal", routing_key="priority.normal", ..., prefetch_count=10)

# Low priority
QueueConfig(name="priority.low", routing_key="priority.low", ..., prefetch_count=1)
```

### Pattern: Domain Contexts

```python
# Customers
QueueConfig(
    name="customers.queue",
    routing_key="domain.customers",
    task_handlers={"customer_created": ..., "customer_updated": ...},
)

# Orders
QueueConfig(
    name="orders.queue",
    routing_key="domain.orders",
    task_handlers={"order_placed": ..., "order_shipped": ...},
)
```

## Prefetch Count Guide

| Value | Processing | Use Case | Example |
|-------|-----------|----------|---------|
| 1 | Serial | Heavy tasks, exclusive resources | Reports, migrations |
| 5-10 | Moderate | Standard workload | API calls, emails |
| 20+ | High | Lightweight, high throughput | Notifications, logging |

## Message Format

```python
{
    "task": "task_name",        # Required: matches handler key
    "customer_id": 123,          # Optional: business context
    "payload": {                 # Optional: task-specific data
        "key": "value"
    }
}
```

## Publishing Examples

```python
from app.broker import publish_task

# Basic
await publish_task(
    {"task": "send_email", "customer_id": 123},
    routing_key="tasks.main"
)

# With payload
await publish_task(
    {
        "task": "send_email",
        "customer_id": 123,
        "payload": {
            "to": "user@example.com",
            "subject": "Welcome",
            "body": "Hello!"
        }
    },
    routing_key="notifications"
)

# Different exchange
await publish_task(
    {"task": "my_task"},
    routing_key="my_key",
    exchange_name="custom_exchange"
)
```

## Monitoring Commands

```bash
# View RabbitMQ Management UI
open http://localhost:15672
# Username: guest, Password: guest

# Check queue status
docker exec rabbitmq rabbitmqctl list_queues

# View connections
docker exec rabbitmq rabbitmqctl list_connections

# View worker logs
# (Shows which queues are active and message processing)
python -m worker.worker
```

## Troubleshooting

### Messages Not Being Consumed

```bash
# Check RabbitMQ is running
docker-compose ps rabbitmq

# Check queue exists
docker exec rabbitmq rabbitmqctl list_queues

# Check worker logs
python -m worker.worker
```

### Messages Going to DLQ

```bash
# View DLQ messages in RabbitMQ UI
open http://localhost:15672/#/queues/%2F/tasks.dlq

# Check worker error logs
# Look for exception traces in worker output
```

### High Memory Usage

- Reduce `prefetch_count` for queues
- Check for memory leaks in task handlers
- Ensure handlers are async and releasing resources

## File Locations

| Purpose | Location |
|---------|----------|
| Worker code | `worker/worker.py` |
| Task handlers | `worker/tasks/*.py` |
| Publisher | `app/broker.py` |
| Configuration | `QUEUE_CONFIGS` in `worker/worker.py` |
| Examples | `worker/worker_multi_queue_example.py` |
| Tests | `scripts/test_multi_queue.py` |
| Docs | `docs/MULTI_QUEUE_SETUP.md` |

## Key Classes

```python
@dataclass
class QueueConfig:
    name: str                      # Queue name in RabbitMQ
    routing_key: str               # Routing key for binding
    task_handlers: dict[str, Callable]  # Task registry
    prefetch_count: int = 1        # Concurrency control
    exchange_name: str = "tasks"   # Exchange to use
    dlx_exchange_name: str = "tasks.dlx"  # Dead-letter exchange
    dlq_name: str = "tasks.dlq"    # Dead-letter queue
```

## Best Practices

✅ **DO**
- Group related tasks in the same queue
- Set appropriate prefetch based on task characteristics
- Use meaningful routing keys
- Log task progress with queue name
- Make handlers idempotent

❌ **DON'T**
- Set prefetch too high for heavy tasks
- Mix fast and slow tasks in same queue
- Ignore DLQ messages
- Block in async handlers
- Forget to handle exceptions

## Next Steps

1. 📖 Read [MULTI_QUEUE_SETUP.md](./MULTI_QUEUE_SETUP.md) for detailed guide
2. 👀 Review [worker_multi_queue_example.py](../worker/worker_multi_queue_example.py)
3. 🧪 Run [test_multi_queue.py](../scripts/test_multi_queue.py)
4. 🚀 Add your own queues!

---

**Quick Links:**
- [Full Documentation](./MULTI_QUEUE_SETUP.md)
- [Migration Guide](./QUEUE_MIGRATION.md)
- [Example Config](../worker/worker_multi_queue_example.py)
- [Test Script](../scripts/test_multi_queue.py)

