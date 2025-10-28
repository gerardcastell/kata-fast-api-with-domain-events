#!/usr/bin/env python3
"""
Example script demonstrating how to dispatch tasks and process them with the worker.

This script shows the complete workflow:
1. Start LocalStack and worker
2. Dispatch various types of tasks
3. Monitor worker processing
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.dispatcher import TaskDispatcher
from app.shared.infrastructure.sqs.models import TaskPriority


async def dispatch_example_tasks():
    """Dispatch various example tasks to demonstrate the worker."""
    print("🚀 Dispatching example tasks...")

    # Set up LocalStack configuration
    os.environ.update(
        {
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_REGION": "us-east-1",
            "AWS_ENDPOINT_URL": "http://localhost:4566",
            "SQS_QUEUE_URL": "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/task-queue",
        }
    )

    # Create SQS client and dispatcher
    sqs_client = SQSClient()
    dispatcher = TaskDispatcher(sqs_client)

    # Example 1: Data processing task
    print("\n📊 Dispatching data processing task...")
    data_task_id = await dispatcher.dispatch_task(
        task_type="data_processing",
        payload={
            "dataset_id": "dataset_123",
            "operation": "aggregation",
            "parameters": {"group_by": "category", "aggregate": "sum"},
        },
        priority=TaskPriority.HIGH,
        delay_seconds=0,
    )
    if data_task_id:
        print("✅ Data processing task dispatched successfully!")
    else:
        print("❌ Failed to dispatch data processing task")

    # Example 2: Email notification task
    print("\n📧 Dispatching email notification task...")
    email_task_id = await dispatcher.dispatch_task(
        task_type="email_notification",
        payload={
            "to": "user@example.com",
            "subject": "Task Completed",
            "template": "task_completion",
            "data": {"task_id": data_task_id},
        },
        priority=TaskPriority.NORMAL,
        delay_seconds=5,  # Delay by 5 seconds
    )
    if email_task_id:
        print("✅ Email notification task dispatched successfully!")
    else:
        print("❌ Failed to dispatch email notification task")

    # Example 3: Report generation task
    print("\n📈 Dispatching report generation task...")
    report_task_id = await dispatcher.dispatch_task(
        task_type="report_generation",
        payload={
            "report_type": "monthly_summary",
            "date_range": {"start": "2024-01-01", "end": "2024-01-31"},
            "format": "pdf",
            "recipients": ["manager@example.com"],
        },
        priority=TaskPriority.LOW,
        delay_seconds=10,  # Delay by 10 seconds
    )
    if report_task_id:
        print("✅ Report generation task dispatched successfully!")
    else:
        print("❌ Failed to dispatch report generation task")

    print("\n🎯 All tasks dispatched!")
    print(f"   - Data processing task ID: {data_task_id}")
    print(f"   - Email notification task ID: {email_task_id}")
    print(f"   - Report generation task ID: {report_task_id}")

    return [data_task_id, email_task_id, report_task_id]


async def monitor_queue():
    """Monitor the queue to see task processing."""
    print("\n👀 Monitoring queue...")

    # Set up LocalStack configuration
    os.environ.update(
        {
            "AWS_ACCESS_KEY_ID": "test",
            "AWS_SECRET_ACCESS_KEY": "test",
            "AWS_REGION": "us-east-1",
            "AWS_ENDPOINT_URL": "http://localhost:4566",
            "SQS_QUEUE_URL": "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/task-queue",
        }
    )

    sqs_client = SQSClient()

    # Get queue attributes to see message count
    attributes = await sqs_client.get_queue_attributes()
    message_count = attributes.get("ApproximateNumberOfMessages", "0")

    print("📊 Queue status:")
    print(f"   - Messages in queue: {message_count}")
    print(
        f"   - Messages in flight: {attributes.get('ApproximateNumberOfMessagesNotVisible', '0')}"
    )
    print(f"   - Messages delayed: {attributes.get('ApproximateNumberOfMessagesDelayed', '0')}")

    return int(message_count)


async def main():
    """Main example function."""
    print("=" * 60)
    print("🧪 SQS Worker Example")
    print("=" * 60)
    print("This example demonstrates:")
    print("1. Dispatching different types of tasks")
    print("2. Monitoring queue status")
    print("3. Worker processing workflow")
    print("=" * 60)

    try:
        # Dispatch example tasks
        task_ids = await dispatch_example_tasks()

        # Monitor initial queue status
        initial_count = await monitor_queue()

        print("\n💡 Next steps:")
        print("   1. Start the worker: make worker")
        print("   2. Monitor worker logs: make worker-logs")
        print("   3. Check queue status: make sqs-test")

        print("\n🎉 Example completed!")
        print(f"   Dispatched {len(task_ids)} tasks")
        print(f"   Queue has {initial_count} messages")

    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("💡 Make sure LocalStack is running: make localstack")


if __name__ == "__main__":
    asyncio.run(main())
