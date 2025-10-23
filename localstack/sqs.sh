#!/usr/bin/env bash
echo "########### Setting up localstack profile ###########"

set -euo pipefail

LOCALSTACK_HOST=localhost
AWS_REGION=us-east-1

create_queue() {
  local QUEUE_NAME=$1
  local DLQ_NAME="dlq-${QUEUE_NAME}"

  echo "Creating DLQ: ${DLQ_NAME}"
  awslocal sqs create-queue \
    --queue-name ${DLQ_NAME} \
    --region ${AWS_REGION} \
    --attributes VisibilityTimeout=30

  echo "Creating main queue: ${QUEUE_NAME}"
  awslocal sqs create-queue \
    --queue-name ${QUEUE_NAME} \
    --region ${AWS_REGION} \
    --attributes VisibilityTimeout=30

  local DLQ_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url http://${LOCALSTACK_HOST}:4566/0000000000000/${DLQ_NAME} \
    --attribute-names QueueArn \
    --query Attributes.QueueArn \
    --output text)

  echo "Setting RedrivePolicy for ${QUEUE_NAME} → ${DLQ_NAME}"
  awslocal sqs set-queue-attributes \
    --queue-url http://${LOCALSTACK_HOST}:4566/000000000000/${QUEUE_NAME} \
    --attributes "{\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"${DLQ_ARN}\\\",\\\"maxReceiveCount\\\":\\\"1\\\"}\"}"
}

create_queue "test-queue"

echo "All queues:"
awslocal --endpoint-url=http://${LOCALSTACK_HOST}:4566 sqs list-queues
