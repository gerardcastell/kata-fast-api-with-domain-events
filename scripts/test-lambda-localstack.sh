#!/bin/bash
set -e

# Script to test Lambda function with LocalStack
# Usage: ./scripts/test-lambda-localstack.sh

echo "=========================================="
echo "Testing Lambda Function with LocalStack"
echo "=========================================="
echo ""

# Configuration
FUNCTION_NAME="events-sqs-processor"
AWS_REGION="us-east-1"

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=${AWS_REGION}

echo "🧪 Test 1: Direct Lambda Invocation"
echo "-----------------------------------"
echo "Creating test event payload..."

# Create a test event that mimics SQS event structure
TEST_EVENT=$(cat <<EOF
{
  "Records": [
    {
      "messageId": "test-message-1",
      "receiptHandle": "test-receipt-handle",
      "body": "{\"task_id\": \"$(uuidgen)\", \"task_type\": \"data_processing\", \"priority\": \"normal\", \"payload\": {\"data\": [1, 2, 3, 4, 5], \"processing_type\": \"aggregation\"}, \"retry_count\": 0, \"max_retries\": 3, \"delay_seconds\": 0, \"timestamp\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"}",
      "attributes": {
        "ApproximateReceiveCount": "1",
        "SentTimestamp": "$(date +%s)000",
        "SenderId": "AIDAIT2UOQQY3AUEKVGXU",
        "ApproximateFirstReceiveTimestamp": "$(date +%s)000"
      },
      "messageAttributes": {},
      "md5OfBody": "test-md5",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:us-east-1:000000000000:task-queue",
      "awsRegion": "us-east-1"
    }
  ]
}
EOF
)

echo "Invoking Lambda function: ${FUNCTION_NAME}..."
echo ""

RESPONSE=$(awslocal lambda invoke \
    --function-name ${FUNCTION_NAME} \
    --payload "${TEST_EVENT}" \
    --cli-binary-format raw-in-base64-out \
    /tmp/lambda-response.json)

echo "📊 Invocation Response:"
echo "${RESPONSE}" | jq '.'
echo ""

echo "📄 Lambda Function Response:"
cat /tmp/lambda-response.json | jq '.'
echo ""

# Check if invocation was successful
if echo "${RESPONSE}" | grep -q '"StatusCode": 200'; then
    echo "✅ Test 1 Passed: Lambda invoked successfully"
else
    echo "❌ Test 1 Failed: Lambda invocation error"
    exit 1
fi

echo ""
echo "🧪 Test 2: SQS Triggered Lambda"
echo "-----------------------------------"
echo "Sending message to SQS queue..."

# Send a message to SQS
TASK_ID=$(uuidgen)
MESSAGE_BODY=$(cat <<EOF
{
  "task_id": "${TASK_ID}",
  "task_type": "email_notification",
  "priority": "high",
  "payload": {
    "recipient": "test@example.com",
    "subject": "Lambda Test",
    "body": "Testing Lambda with SQS trigger"
  },
  "retry_count": 0,
  "max_retries": 3,
  "delay_seconds": 0,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
)

awslocal sqs send-message \
    --queue-url http://localhost:4566/000000000000/task-queue \
    --message-body "${MESSAGE_BODY}"

echo "✅ Message sent to SQS with task_id: ${TASK_ID}"
echo ""
echo "⏳ Waiting 5 seconds for Lambda to process..."
sleep 5

echo ""
echo "📋 Checking Lambda logs..."
echo "(Note: In LocalStack, logs may be limited)"

# Try to get logs (LocalStack Community may have limited logging)
awslocal logs tail /aws/lambda/${FUNCTION_NAME} --since 1m || echo "⚠️  Log retrieval not available in LocalStack Community"

echo ""
echo "✅ Test 2 Complete: Check worker.log or Lambda container logs for processing details"

echo ""
echo "🧪 Test 3: Batch Processing"
echo "-----------------------------------"
echo "Sending multiple messages to SQS..."

# Send multiple messages
for i in {1..3}; do
    TASK_ID=$(uuidgen)
    MESSAGE_BODY=$(cat <<EOF
{
  "task_id": "${TASK_ID}",
  "task_type": "report_generation",
  "priority": "normal",
  "payload": {
    "report_type": "test_report_${i}",
    "format": "pdf"
  },
  "retry_count": 0,
  "max_retries": 3,
  "delay_seconds": 0,
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
)

    awslocal sqs send-message \
        --queue-url http://localhost:4566/000000000000/task-queue \
        --message-body "${MESSAGE_BODY}" >/dev/null

    echo "   Sent message ${i}/3 (task_id: ${TASK_ID})"
done

echo ""
echo "✅ Batch messages sent"
echo "⏳ Waiting 5 seconds for Lambda to process..."
sleep 5

echo ""
echo "📊 Checking queue status..."
QUEUE_ATTRS=$(awslocal sqs get-queue-attributes \
    --queue-url http://localhost:4566/000000000000/task-queue \
    --attribute-names ApproximateNumberOfMessages,ApproximateNumberOfMessagesNotVisible)

echo "${QUEUE_ATTRS}" | jq '.Attributes'

echo ""
echo "✅ Test 3 Complete"

echo ""
echo "=========================================="
echo "🎉 All Tests Complete!"
echo "=========================================="
echo ""
echo "📝 Summary:"
echo "   ✅ Direct Lambda invocation: Success"
echo "   ✅ SQS triggered Lambda: Message sent"
echo "   ✅ Batch processing: Multiple messages sent"
echo ""
echo "💡 Tips:"
echo "   - Check Lambda container logs: docker logs -f <lambda-container-id>"
echo "   - View LocalStack logs: make localstack-logs"
echo "   - Monitor queue: awslocal sqs get-queue-attributes ..."
echo ""
