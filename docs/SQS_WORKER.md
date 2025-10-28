# SQS Worker Implementation

This implementation provides a complete SQS-based worker system for processing async tasks using boto3.

## Features

- **Async SQS Client**: Non-blocking SQS operations using boto3
- **Task Processing**: Configurable worker with concurrent task processing
- **Retry Logic**: Automatic retry with exponential backoff
- **Graceful Shutdown**: Proper cleanup and task completion
- **Health Monitoring**: Queue monitoring and health checks
- **Dependency Injection**: Integrated with the existing DI container
- **Example Tasks**: Ready-to-use task processors

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Task          │    │   SQS           │    │   Worker        │
│   Dispatcher    │───▶│   Queue         │───▶│   Processors    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### 1. Task Models (`models.py`)

- `TaskMessage`: SQS message structure
- `TaskResult`: Task execution result
- `TaskStatus`: Task status enumeration
- `TaskPriority`: Task priority levels
- `WorkerConfig`: Worker configuration

### 2. SQS Client (`client.py`)

- Async SQS operations using boto3
- Message sending and receiving
- Visibility timeout management
- Error handling and logging

### 3. Worker (`worker.py`)

- Main worker implementation
- Concurrent task processing
- Retry logic with exponential backoff
- Graceful shutdown handling
- Health monitoring

### 4. Task Dispatcher (`dispatcher.py`)

- Service for dispatching tasks to SQS
- Single and batch task dispatch
- Priority and delay support

### 5. Example Tasks (`tasks.py`)

- `DataProcessingTask`: Long-running data processing
- `EmailNotificationTask`: Email sending with retry logic
- `ReportGenerationTask`: Report generation simulation

## Configuration

Add the following environment variables to your `.env` file:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1

# SQS Configuration
SQS_QUEUE_URL=https://sqs.us-east-1.amazonaws.com/123456789012/your-queue
SQS_MAX_MESSAGES=10
SQS_WAIT_TIME_SECONDS=20
SQS_VISIBILITY_TIMEOUT=300
```

## Usage

### 1. Start the Worker

```bash
python scripts/worker.py
```

### 2. Dispatch Tasks

```python
from app.shared.infrastructure.sqs.dispatcher import TaskDispatcher
from app.shared.infrastructure.sqs.models import TaskPriority

# Get dispatcher from DI container
dispatcher = container.task_dispatcher()

# Dispatch a single task
task_id = await dispatcher.dispatch_task(
    task_type="data_processing",
    payload={"data": [1, 2, 3, 4, 5], "processing_type": "aggregation"},
    priority=TaskPriority.NORMAL,
    max_retries=3,
)

# Dispatch batch tasks
tasks = [
    ("data_processing", {"data": [1, 2, 3], "processing_type": "transformation"}),
    ("email_notification", {"recipient": "user@example.com", "subject": "Hello"}),
]
task_ids = await dispatcher.dispatch_batch_tasks(tasks)
```

### 3. Create Custom Task Processors

```python
from app.shared.infrastructure.sqs.worker import TaskProcessor
from app.shared.infrastructure.sqs.models import TaskMessage, TaskResult, TaskStatus

class CustomTask(TaskProcessor):
    def __init__(self):
        super().__init__("custom_task")

    async def process(self, message: TaskMessage) -> TaskResult:
        try:
            # Your task logic here
            data = message.payload.get("data")

            # Process the data
            result = await self._process_data(data)

            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.COMPLETED,
                result={"processed": result},
            )
        except Exception as e:
            return TaskResult(
                task_id=message.task_id,
                status=TaskStatus.FAILED,
                error_message=str(e),
            )

    async def _process_data(self, data):
        # Your processing logic
        await asyncio.sleep(5)  # Simulate work
        return f"Processed: {data}"
```

### 4. Register Custom Processors

```python
from app.shared.infrastructure.sqs.worker import SQSWorker

worker = SQSWorker(sqs_client, worker_config)
worker.register_processor(CustomTask())
```

## Testing

### Dispatch Test Tasks

```bash
python scripts/dispatch_tasks.py
```

This will dispatch sample tasks to test the worker system.

## Monitoring

The worker provides built-in monitoring:

- **Health Checks**: Periodic queue attribute monitoring
- **Task Tracking**: Active task count and processing time
- **Error Logging**: Comprehensive error logging with context
- **Metrics**: Processing statistics and performance metrics

## Error Handling

- **Retry Logic**: Automatic retry with exponential backoff
- **Dead Letter Queue**: Failed tasks after max retries
- **Graceful Degradation**: Continues processing despite individual task failures
- **Comprehensive Logging**: Detailed error information for debugging

## Performance Considerations

- **Concurrent Processing**: Configurable max concurrent tasks
- **Batch Operations**: Efficient batch message processing
- **Connection Pooling**: Reused SQS client connections
- **Memory Management**: Proper cleanup of completed tasks

## Security

- **IAM Roles**: Use IAM roles instead of access keys when possible
- **Queue Policies**: Restrict queue access with appropriate policies
- **Message Encryption**: Enable SQS encryption for sensitive data
- **VPC Endpoints**: Use VPC endpoints for private communication

## Deployment

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .

RUN pip install -e .

CMD ["python", "scripts/worker.py"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sqs-worker
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sqs-worker
  template:
    metadata:
      labels:
        app: sqs-worker
    spec:
      containers:
        - name: worker
          image: your-registry/sqs-worker:latest
          env:
            - name: SQS_QUEUE_URL
              valueFrom:
                secretKeyRef:
                  name: sqs-config
                  key: queue-url
            - name: AWS_REGION
              value: 'us-east-1'
```

## Troubleshooting

### Common Issues

1. **Queue Not Found**: Verify SQS_QUEUE_URL is correct
2. **Permission Denied**: Check AWS credentials and IAM permissions
3. **Messages Not Processing**: Check worker logs and queue visibility timeout
4. **High Memory Usage**: Reduce max_concurrent_tasks or increase polling interval

### Debugging

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python scripts/worker.py
```

Check queue attributes:

```python
attributes = await sqs_client.get_queue_attributes()
print(f"Messages in queue: {attributes.get('ApproximateNumberOfMessages')}")
```
