#!/bin/bash
set -e

# Script to build and deploy Lambda to LocalStack
# Usage: ./scripts/deploy-lambda-localstack.sh

echo "=========================================="
echo "LocalStack Lambda Deployment Script"
echo "=========================================="
echo ""

# Configuration
FUNCTION_NAME="events-sqs-processor"
IMAGE_NAME="events-fastapi-lambda-local"
IMAGE_TAG="latest"
AWS_ENDPOINT_URL="http://localhost:4566"
AWS_REGION="us-east-1"
LAMBDA_ROLE="arn:aws:iam::000000000000:role/lambda-execution-role"

# Set AWS credentials for LocalStack
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test
export AWS_DEFAULT_REGION=${AWS_REGION}

echo "🔍 Checking if LocalStack is running..."
if ! curl -f ${AWS_ENDPOINT_URL}/_localstack/health >/dev/null 2>&1; then
    echo "❌ LocalStack is not running!"
    echo "💡 Start LocalStack with: make localstack"
    exit 1
fi
echo "✅ LocalStack is running"
echo ""

# Step 1: Build the Lambda Docker image
echo "🏗️  Building Lambda Docker image..."
docker build -f lambda/Dockerfile -t ${IMAGE_NAME}:${IMAGE_TAG} .
echo "✅ Build completed"
echo ""

# Step 2: Create IAM role (LocalStack doesn't enforce IAM, but Lambda needs a role ARN)
echo "🔐 Creating IAM role..."
awslocal iam create-role \
    --role-name lambda-execution-role \
    --assume-role-policy-document '{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }' >/dev/null 2>&1 || echo "   (Role may already exist, continuing...)"
echo "✅ IAM role ready"
echo ""

# Step 3: Check if Lambda function exists
echo "🔍 Checking if Lambda function exists..."
if awslocal lambda get-function --function-name ${FUNCTION_NAME} >/dev/null 2>&1; then
    echo "📝 Function exists, deleting old version..."
    awslocal lambda delete-function --function-name ${FUNCTION_NAME}
    echo "✅ Old function deleted"
fi
echo ""

# Step 4: Check LocalStack edition
echo "🔍 Checking LocalStack edition..."
LOCALSTACK_EDITION=$(curl -s http://localhost:4566/_localstack/health | jq -r '.edition // "community"')
echo "   LocalStack edition: ${LOCALSTACK_EDITION}"

if [ "${LOCALSTACK_EDITION}" != "pro" ]; then
    echo ""
    echo "⚠️  WARNING: Container images require LocalStack Pro!"
    echo "   Current edition: ${LOCALSTACK_EDITION}"
    echo ""
    echo "   Options:"
    echo "   1. Use worker mode instead: make worker"
    echo "   2. Get LocalStack Pro: https://localstack.cloud"
    echo "   3. Test on AWS Lambda: ./scripts/deploy-lambda-ecr.sh"
    echo ""
    echo "   See docs/LAMBDA.md for troubleshooting and alternatives"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
fi

# Step 5: Create Lambda function
echo "🚀 Creating Lambda function..."
awslocal lambda create-function \
    --function-name ${FUNCTION_NAME} \
    --package-type Image \
    --code ImageUri=${IMAGE_NAME}:${IMAGE_TAG} \
    --role ${LAMBDA_ROLE} \
    --timeout 900 \
    --memory-size 512 \
    --environment "Variables={
        PYTHONPATH=/var/task,
        AWS_ENDPOINT_URL=http://localstack:4566,
        AWS_REGION=${AWS_REGION},
        LOG_LEVEL=DEBUG
    }" || {
    echo ""
    echo "❌ Lambda deployment failed!"
    echo ""
    if [ "${LOCALSTACK_EDITION}" != "pro" ]; then
        echo "   This is likely because container images require LocalStack Pro."
        echo "   Recommendation: Use worker mode for local testing:"
        echo "   → make worker"
    fi
    exit 1
}

echo "✅ Lambda function created"
echo ""

# Step 6: Get SQS Queue ARN
echo "📋 Getting SQS queue ARN..."
QUEUE_URL=$(awslocal sqs get-queue-url --queue-name task-queue --query 'QueueUrl' --output text)
QUEUE_ARN=$(awslocal sqs get-queue-attributes \
    --queue-url "${QUEUE_URL}" \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' \
    --output text)

echo "   Queue URL: ${QUEUE_URL}"
echo "   Queue ARN: ${QUEUE_ARN}"
echo ""

# Step 7: Delete existing event source mapping if it exists
echo "🔗 Checking for existing event source mappings..."
EXISTING_MAPPING=$(awslocal lambda list-event-source-mappings \
    --function-name ${FUNCTION_NAME} \
    --query 'EventSourceMappings[0].UUID' \
    --output text 2>/dev/null || echo "")

if [ -n "$EXISTING_MAPPING" ] && [ "$EXISTING_MAPPING" != "None" ]; then
    echo "   Deleting existing mapping: ${EXISTING_MAPPING}"
    awslocal lambda delete-event-source-mapping --uuid ${EXISTING_MAPPING}
fi
echo ""

# Step 8: Create event source mapping (SQS trigger)
echo "🔗 Creating SQS event source mapping..."
awslocal lambda create-event-source-mapping \
    --function-name ${FUNCTION_NAME} \
    --event-source-arn ${QUEUE_ARN} \
    --batch-size 10 \
    --enabled

echo "✅ Event source mapping created"
echo ""

# Step 9: Verify setup
echo "🔍 Verifying Lambda setup..."
awslocal lambda get-function --function-name ${FUNCTION_NAME} --query 'Configuration.[FunctionName,State,LastUpdateStatus]' --output table

echo ""
echo "=========================================="
echo "✅ Lambda Deployment Complete!"
echo "=========================================="
echo ""
echo "📝 Lambda Details:"
echo "   Function Name: ${FUNCTION_NAME}"
echo "   Queue ARN: ${QUEUE_ARN}"
echo "   Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "🧪 Test your Lambda:"
echo "   1. Send message to SQS:"
echo "      make sqs-send-test"
echo ""
echo "   2. Or use dispatch script:"
echo "      uv run python scripts/dispatch_tasks.py"
echo ""
echo "   3. Check Lambda logs:"
echo "      make lambda-logs"
echo ""
echo "   4. Test Lambda directly:"
echo "      make lambda-test-invoke"
echo ""
echo "🎉 Ready to test!"
