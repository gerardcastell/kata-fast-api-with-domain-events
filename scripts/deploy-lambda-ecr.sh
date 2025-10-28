#!/bin/bash
set -e

# Script to build and push Lambda Docker image to AWS ECR
# Usage: ./scripts/deploy-lambda-ecr.sh [AWS_ACCOUNT_ID] [AWS_REGION] [REPOSITORY_NAME]

# Configuration
AWS_ACCOUNT_ID=${1:-$(aws sts get-caller-identity --query Account --output text)}
AWS_REGION=${2:-us-east-1}
REPOSITORY_NAME=${3:-events-fastapi-lambda}
IMAGE_TAG=${4:-latest}

# Derived values
ECR_REPOSITORY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
FULL_IMAGE_NAME="${ECR_REPOSITORY}/${REPOSITORY_NAME}:${IMAGE_TAG}"

echo "=========================================="
echo "AWS Lambda ECR Deployment Script"
echo "=========================================="
echo "AWS Account ID: ${AWS_ACCOUNT_ID}"
echo "AWS Region: ${AWS_REGION}"
echo "Repository: ${REPOSITORY_NAME}"
echo "Image Tag: ${IMAGE_TAG}"
echo "Full Image: ${FULL_IMAGE_NAME}"
echo "=========================================="
echo ""

# Step 1: Check if repository exists, create if not
echo "📦 Checking if ECR repository exists..."
if ! aws ecr describe-repositories --repository-names ${REPOSITORY_NAME} --region ${AWS_REGION} >/dev/null 2>&1; then
    echo "📦 Creating ECR repository: ${REPOSITORY_NAME}"
    aws ecr create-repository \
        --repository-name ${REPOSITORY_NAME} \
        --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256

    echo "✅ Repository created successfully"
else
    echo "✅ Repository already exists"
fi

# Step 2: Login to ECR
echo ""
echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPOSITORY}
echo "✅ Logged in successfully"

# Step 3: Build the Lambda image
echo ""
echo "🏗️  Building Lambda Docker image..."
docker build -f lambda/Dockerfile -t ${REPOSITORY_NAME}:${IMAGE_TAG} .
echo "✅ Build completed"

# Step 4: Tag the image
echo ""
echo "🏷️  Tagging image for ECR..."
docker tag ${REPOSITORY_NAME}:${IMAGE_TAG} ${FULL_IMAGE_NAME}
echo "✅ Image tagged"

# Step 5: Push to ECR
echo ""
echo "⬆️  Pushing image to ECR..."
docker push ${FULL_IMAGE_NAME}
echo "✅ Push completed"

# Step 6: Get image digest
echo ""
echo "🔍 Getting image digest..."
IMAGE_DIGEST=$(aws ecr describe-images \
    --repository-name ${REPOSITORY_NAME} \
    --image-ids imageTag=${IMAGE_TAG} \
    --region ${AWS_REGION} \
    --query 'imageDetails[0].imageDigest' \
    --output text)

echo "✅ Image pushed successfully!"
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo "Repository URI: ${ECR_REPOSITORY}/${REPOSITORY_NAME}"
echo "Image Tag: ${IMAGE_TAG}"
echo "Image Digest: ${IMAGE_DIGEST}"
echo "Full Image URI: ${FULL_IMAGE_NAME}"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo "1. Create or update Lambda function with this image:"
echo ""
echo "   aws lambda create-function \\"
echo "     --function-name events-sqs-processor \\"
echo "     --package-type Image \\"
echo "     --code ImageUri=${FULL_IMAGE_NAME} \\"
echo "     --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-execution-role \\"
echo "     --timeout 900 \\"
echo "     --memory-size 512 \\"
echo "     --region ${AWS_REGION}"
echo ""
echo "2. Or update existing function:"
echo ""
echo "   aws lambda update-function-code \\"
echo "     --function-name events-sqs-processor \\"
echo "     --image-uri ${FULL_IMAGE_NAME} \\"
echo "     --region ${AWS_REGION}"
echo ""
echo "3. Configure SQS trigger:"
echo ""
echo "   aws lambda create-event-source-mapping \\"
echo "     --function-name events-sqs-processor \\"
echo "     --event-source-arn arn:aws:sqs:${AWS_REGION}:${AWS_ACCOUNT_ID}:task-queue \\"
echo "     --batch-size 10 \\"
echo "     --enabled \\"
echo "     --region ${AWS_REGION}"
echo ""
echo "🎉 Deployment complete!"
