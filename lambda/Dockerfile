# AWS Lambda Container Image Dockerfile
# This image is designed to be deployed to AWS Lambda via ECR
# Uses the same base image as the server for consistency

FROM python:3.12-slim

# Set Lambda-specific environment variables
ENV LAMBDA_TASK_ROOT=/var/task \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/var/task

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install --no-cache-dir uv

# Install AWS Lambda Runtime Interface Client
RUN pip install --no-cache-dir awslambdaric

# Set work directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application code (needed by lambda handler for task processing)
COPY ./app ./app

# Copy lambda handler
COPY ./lambda/lambda_handler.py ./

# Set the CMD to your handler using the Lambda Runtime Interface Client
# Lambda will invoke: lambda_handler.handler(event, context)
ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "lambda_handler.handler" ]
