# LocalStack SQS Testing Guide

This guide explains how to use LocalStack for local SQS testing with your FastAPI application.

## Overview

LocalStack provides a fully functional local AWS cloud stack that includes SQS services. This allows you to test your SQS implementation locally without needing actual AWS credentials or resources.

## Setup

### 1. Environment Configuration

Copy the `local.env` file to `.env` and modify as needed:

```bash
cp local.env .env
```

The key LocalStack configuration variables are:

```bash
# LocalStack SQS Configuration
aws_access_key_id=test
aws_secret_access_key=test
aws_region=us-east-1
sqs_queue_url=http://localstack:4566/000000000000/task-queue
sqs_max_messages=10
sqs_wait_time_seconds=20
sqs_visibility_timeout=300
```

### 2. Start LocalStack

Start LocalStack along with your application:

```bash
# Start all services including LocalStack
docker-compose up localstack

# Or start everything
docker-compose up
```

### 3. Queue Initialization

The SQS queues are automatically created when LocalStack starts using the initialization script at `scripts/localstack-init.sh`. This script:

- Creates a main task queue (`task-queue`)
- Creates a dead letter queue (`task-queue-dlq`)
- Configures the dead letter queue policy
- Sets appropriate queue attributes

## Usage

### Running the Application

#### Development Mode

```bash
# Start with hot reload
docker-compose up app-dev

# The app will be available at http://localhost:8001
```

#### Production Mode

```bash
# Start production service
docker-compose up app

# The app will be available at http://localhost:8000
```

#### Debug Mode

```bash
# Start with debugger
docker-compose up app-debug

# The app will be available at http://localhost:8002
# Debug port: 5678
```

### Testing

#### Run Tests with LocalStack

```bash
# Run tests with LocalStack
docker-compose -f docker-compose.test.yml up --build

# Or run tests locally (requires LocalStack running)
docker-compose up localstack
# In another terminal:
uv run pytest tests/ -v
```

#### Manual Testing

You can test SQS functionality using the AWS CLI with LocalStack:

```bash
# Set up AWS CLI for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:4566

# List queues
awslocal sqs list-queues

# Send a test message
awslocal sqs send-message \
    --queue-url http://localhost:4566/000000000000/task-queue \
    --message-body '{"task_type": "test", "task_id": "123", "priority": "normal"}'

# Receive messages
awslocal sqs receive-message \
    --queue-url http://localhost:4566/000000000000/task-queue
```

### Using the Dispatch Script

Test your task dispatching:

```bash
# Start LocalStack and your app
docker-compose up localstack app-dev

# In another terminal, run the dispatch script
uv run python scripts/dispatch_tasks.py
```

### Using the Worker

#### Docker Compose Worker Service

Start the worker as a Docker service:

```bash
# Start LocalStack and worker
make localstack
make worker

# View worker logs
make worker-logs

# Stop worker
make worker-stop
```

#### Manual Worker Script

Test your worker manually:

```bash
# Start LocalStack and your app
docker-compose up localstack app-dev

# In another terminal, run the worker
uv run python scripts/worker.py
```

### Worker Monitoring

The worker service includes several monitoring features:

- **Health Checks**: Docker health check monitors worker.log file
- **Logging**: Comprehensive logging to both console and worker.log file
- **Graceful Shutdown**: Handles SIGTERM and SIGINT signals properly
- **Task Tracking**: Monitors active tasks and processing times
- **Retry Logic**: Automatic retry with exponential backoff for failed tasks

Monitor worker status:

```bash
# Check worker container status
docker-compose ps worker

# View real-time logs
make worker-logs

# Check worker health
docker-compose exec worker python -c "import os; print('Worker log exists:', os.path.exists('/app/worker.log'))"
```

## LocalStack Web Interface

LocalStack provides a web interface for monitoring and debugging:

- **URL**: http://localhost:4566/\_localstack/health
- **SQS Management**: Use the AWS CLI or AWS SDK as shown above

## Configuration Details

### Queue Configuration

The initialization script creates queues with the following attributes:

- **Visibility Timeout**: 300 seconds (5 minutes)
- **Message Retention**: 14 days
- **Receive Wait Time**: 20 seconds (long polling)
- **Dead Letter Queue**: Configured with max receive count of 3

### Environment Variables

| Variable                 | Default                                          | Description                |
| ------------------------ | ------------------------------------------------ | -------------------------- |
| `AWS_ACCESS_KEY_ID`      | `test`                                           | LocalStack access key      |
| `AWS_SECRET_ACCESS_KEY`  | `test`                                           | LocalStack secret key      |
| `AWS_REGION`             | `us-east-1`                                      | AWS region                 |
| `SQS_QUEUE_URL`          | `http://localstack:4566/000000000000/task-queue` | Main task queue URL        |
| `SQS_MAX_MESSAGES`       | `10`                                             | Max messages per receive   |
| `SQS_WAIT_TIME_SECONDS`  | `20`                                             | Long polling wait time     |
| `SQS_VISIBILITY_TIMEOUT` | `300`                                            | Message visibility timeout |

## Available Commands

### LocalStack Commands

```bash
make localstack       # Start LocalStack SQS service
make localstack-logs  # View LocalStack logs
make localstack-stop  # Stop LocalStack service
make sqs-test         # Run SQS functionality tests
```

### Application Commands

```bash
make dev              # Start development environment
make debug            # Start debug environment
```

### Worker Commands

```bash
make worker           # Start SQS worker service
make worker-logs      # View worker logs
make worker-stop      # Stop worker service
make worker-shell     # Access worker container shell
```

## Troubleshooting

### Common Issues

1. **LocalStack not ready**: Wait for the health check to pass before starting your app
2. **Queue not found**: Ensure the initialization script ran successfully
3. **Connection refused**: Check that LocalStack is running on port 4566

### Debugging

Enable debug logging:

```bash
# Set debug environment variable
export DEBUG=1

# Check LocalStack logs
docker-compose logs localstack

# Check application logs
docker-compose logs app-dev
```

### Reset LocalStack

To reset LocalStack and recreate queues:

```bash
# Stop and remove LocalStack container
docker-compose down localstack

# Remove LocalStack data volume
docker volume rm $(docker volume ls -q | grep localstack)

# Start again
docker-compose up localstack
```

## Production Considerations

When deploying to production:

1. Replace LocalStack configuration with real AWS credentials
2. Update queue URLs to use real AWS SQS endpoints
3. Configure proper IAM roles and policies
4. Set up CloudWatch monitoring
5. Configure dead letter queues for error handling

## Additional Resources

- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS SQS Documentation](https://docs.aws.amazon.com/sqs/)
- [boto3 SQS Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sqs.html)
