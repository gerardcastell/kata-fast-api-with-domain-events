#!/bin/bash
set -e

# Script to package Lambda as ZIP for LocalStack Community Edition
# Note: LocalStack Community Edition only supports ZIP deployments, not container images

echo "=========================================="
echo "Lambda ZIP Packaging for LocalStack Community"
echo "=========================================="
echo ""

# Configuration
FUNCTION_NAME="events-sqs-processor"
ZIP_FILE="lambda-function.zip"
PACKAGE_DIR="lambda-package"

# Clean up previous package
echo "🧹 Cleaning up previous package..."
rm -rf ${PACKAGE_DIR}
rm -f ${ZIP_FILE}
mkdir -p ${PACKAGE_DIR}

echo "📦 Installing dependencies..."
# Install dependencies to package directory
uv pip install --target ${PACKAGE_DIR} \
    boto3 \
    pydantic-settings \
    --no-deps

# Install dependencies recursively
uv pip install --target ${PACKAGE_DIR} \
    $(uv pip list --format json | jq -r '.[] | select(.name != "pip" and .name != "setuptools") | "\(.name)==\(.version)"')

echo "📋 Copying application code..."
# Copy app directory
cp -r app ${PACKAGE_DIR}/

# Copy lambda handler
cp lambda/lambda_handler.py ${PACKAGE_DIR}/

# Create a simplified handler that works in Lambda environment
cat > ${PACKAGE_DIR}/lambda_handler.py << 'EOF'
#!/usr/bin/env python3
"""
Lambda handler for ZIP deployment.
"""
import json
import logging
import sys
from pathlib import Path

# Ensure app is importable
sys.path.insert(0, str(Path(__file__).parent))

from lambda_handler import handler as original_handler

def handler(event, context):
    """Proxy handler for ZIP deployment."""
    return original_handler(event, context)
EOF

echo "📦 Creating ZIP file..."
cd ${PACKAGE_DIR}
zip -r ../${ZIP_FILE} . -q
cd ..

echo "✅ ZIP package created: ${ZIP_FILE}"
echo "📊 Package size: $(du -h ${ZIP_FILE} | cut -f1)"

# Check if package is too large (>50MB unzipped, >250MB zipped)
PACKAGE_SIZE=$(du -m ${ZIP_FILE} | cut -f1)
if [ ${PACKAGE_SIZE} -gt 250 ]; then
    echo "⚠️  WARNING: Package size exceeds Lambda limits (250MB)"
    echo "   Consider using container images or reducing dependencies"
fi

echo ""
echo "📝 Next steps:"
echo "   1. Deploy to LocalStack:"
echo "      awslocal lambda create-function \\"
echo "        --function-name ${FUNCTION_NAME} \\"
echo "        --runtime python3.12 \\"
echo "        --handler lambda_handler.handler \\"
echo "        --zip-file fileb://${ZIP_FILE} \\"
echo "        --role arn:aws:iam::000000000000:role/lambda-execution-role"
echo ""
echo "   2. Or use: make lambda-deploy-zip"
