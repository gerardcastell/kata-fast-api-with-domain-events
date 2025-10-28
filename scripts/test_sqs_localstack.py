#!/usr/bin/env python3
"""
Simple test script to verify LocalStack SQS functionality.
This script tests the basic SQS operations with LocalStack.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

# Set up LocalStack configuration BEFORE importing SQS client
os.environ.update(
    {
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test",
        "AWS_REGION": "us-east-1",
        "AWS_ENDPOINT_URL": "http://localhost:4566",
        "SQS_QUEUE_URL": "http://sqs.us-east-1.localhost.localstack.cloud:4566/000000000000/task-queue",
    }
)

import uuid

from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.models import TaskMessage, TaskPriority


async def test_sqs_functionality():
    """Test basic SQS functionality with LocalStack."""
    print("🚀 Testing SQS functionality with LocalStack...")

    # Create SQS client
    client = SQSClient()

    try:
        # Test 1: Send a message
        print("\n📤 Test 1: Sending a message...")
        test_message = TaskMessage(
            task_id=uuid.uuid4(),
            task_type="test_task",
            priority=TaskPriority.NORMAL,
            payload={"test": "data", "number": 42},
            delay_seconds=0,
        )

        success = await client.send_message(test_message)
        if success:
            print("✅ Message sent successfully!")
        else:
            print("❌ Failed to send message")
            return False

        # Test 2: Receive messages
        print("\n📥 Test 2: Receiving messages...")
        messages = await client.receive_messages(max_messages=1)

        if messages:
            print(f"✅ Received {len(messages)} message(s)")
            received_message = messages[0]
            print(f"   Task ID: {received_message.task_id}")
            print(f"   Task Type: {received_message.task_type}")
            print(f"   Priority: {received_message.priority}")
            print(f"   Payload: {received_message.payload}")

            # Test 3: Delete message
            print("\n🗑️  Test 3: Deleting message...")
            if hasattr(received_message, "_receipt_handle"):
                delete_success = await client.delete_message(received_message._receipt_handle)
                if delete_success:
                    print("✅ Message deleted successfully!")
                else:
                    print("❌ Failed to delete message")
                    return False
            else:
                print("⚠️  No receipt handle found, skipping delete test")
        else:
            print("❌ No messages received")
            return False

        # Test 4: Get queue attributes
        print("\n📊 Test 4: Getting queue attributes...")
        attributes = await client.get_queue_attributes()
        if attributes:
            print("✅ Queue attributes retrieved:")
            for key, value in attributes.items():
                print(f"   {key}: {value}")
        else:
            print("❌ Failed to get queue attributes")
            return False

        print("\n🎉 All tests passed! SQS functionality is working correctly.")
        return True  # noqa: TRY300

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return False


async def main():
    """Main test function."""
    print("=" * 60)
    print("🧪 LocalStack SQS Integration Test")
    print("=" * 60)

    # Check if LocalStack is running
    try:
        import httpx

        response = httpx.get("http://localhost:4566/_localstack/health", timeout=5)
        if response.status_code == 200:
            print("✅ LocalStack is running")
        else:
            print("❌ LocalStack health check failed")
            return
    except Exception as e:
        print(f"❌ Cannot connect to LocalStack: {e}")
        print("💡 Make sure LocalStack is running with: make localstack")
        return

    # Run the tests
    success = await test_sqs_functionality()

    if success:
        print("\n🎯 Test Summary: All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Test Summary: Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
