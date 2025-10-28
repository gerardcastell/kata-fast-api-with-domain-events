#!/bin/bash

# LocalStack SQS initialization script
# This script creates the necessary SQS queues for local development

echo "Initializing LocalStack SQS queues..."

# Set AWS CLI configuration for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=us-east-1
export AWS_ENDPOINT_URL=http://localhost:4566

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
until awslocal sqs list-queues > /dev/null 2>&1; do
    echo "LocalStack not ready yet, waiting..."
    sleep 2
done

echo "LocalStack is ready!"

# Create the main task queue
echo "Creating task queue..."
QUEUE_URL=$(awslocal sqs create-queue \
    --queue-name task-queue \
    --attributes '{
        "VisibilityTimeout": "300",
        "MessageRetentionPeriod": "1209600",
        "ReceiveMessageWaitTimeSeconds": "20",
        "DelaySeconds": "0"
    }' \
    --query 'QueueUrl' \
    --output text)

echo "Task queue created: $QUEUE_URL"

# Create a dead letter queue for failed messages
echo "Creating dead letter queue..."
DLQ_URL=$(awslocal sqs create-queue \
    --queue-name task-queue-dlq \
    --attributes '{
        "VisibilityTimeout": "300",
        "MessageRetentionPeriod": "1209600",
        "ReceiveMessageWaitTimeSeconds": "0",
        "DelaySeconds": "0"
    }' \
    --query 'QueueUrl' \
    --output text)

echo "Dead letter queue created: $DLQ_URL"

# Get the ARN of the dead letter queue
DLQ_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url "$DLQ_URL" \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

echo "Dead letter queue ARN: $DLQ_ARN"

# Update the main queue to use the dead letter queue
echo "Configuring dead letter queue..."
awslocal sqs set-queue-attributes \
    --queue-url "$QUEUE_URL" \
    --attributes "{
        \"RedrivePolicy\": \"{\\\"deadLetterTargetArn\\\":\\\"$DLQ_ARN\\\",\\\"maxReceiveCount\\\":3}\"
    }"

echo "SQS queues initialized successfully!"
echo "Main queue URL: $QUEUE_URL"
echo "Dead letter queue URL: $DLQ_URL"

# List all queues to verify
echo "Available queues:"
awslocal sqs list-queues
