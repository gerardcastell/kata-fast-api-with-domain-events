# Lambda Testing Guide

Complete guide for testing AWS Lambda functions locally with LocalStack and deploying to AWS.

## Overview

This project supports two testing modes for processing SQS messages:

- **Worker Mode** - Continuous polling process (fast development iteration)
- **Lambda Mode** - Event-driven AWS Lambda function (production-accurate testing)

## Quick Start

### Option 1: Worker Mode (Fast Development)

```bash
# Terminal 1: Start LocalStack
make localstack

# Terminal 2: Start Worker
make worker
make worker-logs

# Terminal 3: Send test messages
uv run python scripts/dispatch_tasks.py
```

### Option 2: Lambda Mode (Production Testing)

```bash
# Terminal 1: Start LocalStack
make localstack

# Terminal 2: Deploy Lambda
make lambda-deploy

# Terminal 3: Test Lambda
make lambda-test

# Or dispatch tasks
uv run python scripts/dispatch_tasks.py
```

## Testing Modes Comparison

| Feature              | Worker Mode                 | Lambda Mode               |
| -------------------- | --------------------------- | ------------------------- |
| **Execution**        | Continuous process          | Event-driven              |
| **Code Entry**       | `if __name__ == "__main__"` | `handler(event, context)` |
| **Deployment**       | `make worker`               | `make lambda-deploy`      |
| **Testing Speed**    | ⚡ Instant                  | 🔄 Requires rebuild       |
| **Production Match** | ❌ Different (polling)      | ✅ Exact match            |
| **Logs**             | `worker.log` + stdout       | CloudWatch Logs           |
| **Best For**         | Development & debugging     | Production testing        |

## Lambda Setup

### Prerequisites

- LocalStack running (`make localstack`)
- Docker (for Lambda container images)
- AWS CLI configured with `awslocal` (or `awscli-local`)

### Deploy Lambda to LocalStack

```bash
make lambda-deploy
```

This command:

- Builds the Lambda Docker image
- Creates IAM execution role
- Deploys Lambda function to LocalStack
- Sets up SQS event source mapping

### Available Commands

```bash
# Lambda Management
make lambda-deploy       # Deploy Lambda to LocalStack
make lambda-test         # Run comprehensive tests
make lambda-invoke       # Invoke Lambda directly
make lambda-logs         # View Lambda logs (CloudWatch)
make lambda-cleanup      # Remove Lambda function

# LocalStack Management
make localstack          # Start LocalStack
make localstack-logs     # View logs
make localstack-stop     # Stop LocalStack

# Worker Testing (Alternative)
make worker              # Start worker poller
make worker-logs         # View worker logs
make worker-stop         # Stop worker
```

## Testing Workflows

### Comprehensive Test Suite

```bash
make lambda-test
```

Runs:

- ✅ Direct Lambda invocation test
- ✅ SQS-triggered Lambda test
- ✅ Batch processing test

### Direct Invocation

```bash
make lambda-invoke
```

### Custom Message Testing

```bash
# Using dispatch script
uv run python scripts/dispatch_tasks.py

# Or manually via AWS CLI
awslocal sqs send-message \
    --queue-url http://localhost:4566/000000000000/task-queue \
    --message-body '{
        "task_id": "test-123",
        "task_type": "data_processing",
        "priority": "normal",
        "payload": {"data": [1,2,3,4,5]},
        "retry_count": 0,
        "max_retries": 3,
        "delay_seconds": 0,
        "timestamp": "2025-01-01T00:00:00Z"
    }'
```

## Task Types

The Lambda handler supports these task types:

1. **`data_processing`**

   - Payload: `{"data": [...], "processing_type": "aggregation"}`
   - Simulates data aggregation/transformation

2. **`email_notification`**

   - Payload: `{"recipient": "...", "subject": "...", "body": "..."}`
   - Simulates email sending

3. **`report_generation`**
   - Payload: `{"report_type": "...", "format": "pdf"}`
   - Simulates report generation

## Monitoring

### View Logs

```bash
# LocalStack logs (includes all services)
make localstack-logs

# Lambda CloudWatch logs (requires Lambda invocation first)
make lambda-logs

# Lambda container logs (more reliable for LocalStack)
make lambda-container-logs

# Worker logs (if using worker mode)
make worker-logs
```

### Check Lambda Status

```bash
# List Lambda functions
awslocal lambda list-functions

# Get function details
awslocal lambda get-function --function-name events-sqs-processor

# Check event source mappings
awslocal lambda list-event-source-mappings \
    --function-name events-sqs-processor
```

### Monitor Queue

```bash
# Check messages in queue
awslocal sqs get-queue-attributes \
    --queue-url http://localhost:4566/000000000000/task-queue \
    --attribute-names ApproximateNumberOfMessages

# Check dead letter queue
awslocal sqs receive-message \
    --queue-url http://localhost:4566/000000000000/task-queue-dlq
```

## Troubleshooting

### Lambda Logs Issues

**Problem**: `make lambda-logs` shows "No log group found"

**Solutions**:

1. **Use container logs** (recommended for LocalStack):

   ```bash
   make lambda-container-logs
   ```

2. **Invoke Lambda first**:

   ```bash
   make lambda-invoke
   make lambda-logs
   ```

3. **Send messages to SQS** to trigger Lambda and create logs

**Understanding Log Sources**:

- **CloudWatch Logs** (`make lambda-logs`): Structured logs, available after invocation, limited LocalStack support
- **Container Logs** (`make lambda-container-logs`): Raw container output, always works, best for development

### Lambda Not Processing Messages

1. **Check if Lambda is deployed**:

   ```bash
   awslocal lambda list-functions
   ```

2. **Verify event source mapping**:

   ```bash
   awslocal lambda list-event-source-mappings \
       --function-name events-sqs-processor
   ```

3. **Redeploy if needed**:
   ```bash
   make lambda-cleanup
   make lambda-deploy
   ```

### LocalStack Container Images Limitation

**Problem**: `NotImplementedError: Container images are a Pro feature`

**Solution**: LocalStack Community Edition doesn't support Lambda container images. Use one of these approaches:

1. **Worker Mode** (recommended for development):

   ```bash
   make localstack
   make worker
   ```

2. **LocalStack Pro** (if available):

   - Sign up at [localstack.cloud](https://localstack.cloud)
   - Set `LOCALSTACK_AUTH_TOKEN` environment variable
   - Update `docker-compose.yml` to include the token

3. **Deploy to AWS** (for production validation):

   ```bash
   ./scripts/deploy-lambda-ecr.sh [AWS_ACCOUNT_ID] [AWS_REGION]
   ```

4. **ZIP Deployment** (experimental, limited):
   ```bash
   ./scripts/package-lambda-zip.sh
   # Deploy ZIP package manually
   ```

### LocalStack Health Issues

```bash
# Check LocalStack health
curl http://localhost:4566/_localstack/health

# Restart LocalStack
make localstack-stop
make localstack
```

### Reset Everything

```bash
make lambda-cleanup
make lambda-deploy
make lambda-invoke
make lambda-container-logs
```

## Recommended Workflow

### 1. Development Phase

Use **Worker Mode** for fast iteration:

```bash
make localstack && make worker
# Edit code, test immediately
```

### 2. Pre-Deployment Testing

Switch to **Lambda Mode** for production testing:

```bash
make lambda-deploy
make lambda-test
```

### 3. Production Deployment

Deploy to AWS using the ECR script:

```bash
./scripts/deploy-lambda-ecr.sh [AWS_ACCOUNT_ID] [AWS_REGION]
```

## Common Commands Reference

```bash
# LocalStack
make localstack          # Start LocalStack
make localstack-logs     # View logs
make localstack-stop     # Stop LocalStack

# Lambda Testing
make lambda-deploy       # Deploy Lambda to LocalStack
make lambda-test         # Run all Lambda tests
make lambda-invoke       # Invoke Lambda directly
make lambda-logs         # View Lambda logs
make lambda-cleanup      # Remove Lambda function

# Worker Testing
make worker              # Start worker poller
make worker-logs         # View worker logs
make worker-stop         # Stop worker

# SQS Testing
make sqs-test           # Test basic SQS functionality

# Development
make dev                # Start FastAPI app
make logs               # View app logs

# Help
make help               # Show all commands
```

## Additional Resources

- **[LOCALSTACK.md](LOCALSTACK.md)** - LocalStack setup and worker mode details
- **[SQS_WORKER.md](SQS_WORKER.md)** - Worker implementation details
- **[TESTING.md](TESTING.md)** - General testing guide
- [LocalStack Documentation](https://docs.localstack.cloud/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
