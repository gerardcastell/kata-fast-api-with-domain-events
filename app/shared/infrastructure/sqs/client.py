import asyncio
import json
import logging

import boto3
from botocore.exceptions import ClientError

from app.config.settings import settings
from app.shared.infrastructure.sqs.interface import SQSClientInterface
from app.shared.infrastructure.sqs.models import TaskMessage

logger = logging.getLogger(__name__)


class SQSClient(SQSClientInterface):
    """SQS client implementation using boto3."""

    def __init__(self, queue_url: str | None = None):
        self.queue_url = queue_url or settings.sqs_queue_url
        self._client = None
        self._session = None

    async def _get_client(self):
        """Get or create SQS client."""
        if self._client is None:
            # Run boto3 client creation in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._client = await loop.run_in_executor(None, self._create_client)  # type: ignore[func-returns-value]
        return self._client

    def _create_client(self):
        """Create boto3 SQS client."""
        session_kwargs = {
            "region_name": settings.aws_region,
        }

        # Add credentials if provided
        if settings.aws_access_key_id and settings.aws_secret_access_key:
            session_kwargs.update(
                {
                    "aws_access_key_id": settings.aws_access_key_id,
                    "aws_secret_access_key": settings.aws_secret_access_key,
                }
            )

        self._session = boto3.Session(**session_kwargs)

        client_kwargs = {}
        if settings.aws_endpoint_url:
            client_kwargs["endpoint_url"] = settings.aws_endpoint_url

        return self._session.client("sqs", **client_kwargs)  # type: ignore[attr-defined]

    def _parse_sqs_message(self, sqs_message: dict) -> TaskMessage | None:
        """Parse SQS message into TaskMessage."""
        try:
            # Parse the message body
            message_data = json.loads(sqs_message["Body"])
            task_message = TaskMessage(**message_data)

            # Store receipt handle for later deletion
            task_message.receipt_handle = sqs_message["ReceiptHandle"]

            # Store ApproximateReceiveCount for monitoring (SQS retry count)
            receive_count = sqs_message.get("Attributes", {}).get("ApproximateReceiveCount", "0")
            task_message.approximate_receive_count = int(receive_count)

        except (json.JSONDecodeError, ValueError):
            logger.exception("Failed to parse message:")
            return None
        else:
            return task_message

    async def send_message(self, message: TaskMessage) -> bool:
        """Send a task message to SQS queue."""
        try:
            client = await self._get_client()

            message_body = message.model_dump_json()

            # Prepare message attributes
            message_attributes = {
                "task_type": {"StringValue": message.task_type, "DataType": "String"},
                "priority": {"StringValue": message.priority.value, "DataType": "String"},
                "task_id": {"StringValue": str(message.task_id), "DataType": "String"},
            }

            send_params = {
                "QueueUrl": self.queue_url,
                "MessageBody": message_body,
                "MessageAttributes": message_attributes,
            }

            # Add delay if specified
            if message.delay_seconds > 0:
                send_params["DelaySeconds"] = message.delay_seconds

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: client.send_message(**send_params))

            logger.info(f"Message sent successfully: {response.get('MessageId')}")

        except ClientError:
            logger.exception("Failed to send message:")
            return False
        except Exception:
            logger.exception("Unexpected error sending message:")
            return False
        else:
            return True

    async def receive_messages(self, max_messages: int = 10) -> list[TaskMessage]:
        """Receive task messages from SQS queue."""
        try:
            client = await self._get_client()

            receive_params = {
                "QueueUrl": self.queue_url,
                "MaxNumberOfMessages": min(max_messages, settings.sqs_max_messages),
                "WaitTimeSeconds": settings.sqs_wait_time_seconds,
                "VisibilityTimeout": settings.sqs_visibility_timeout,
                "MessageAttributeNames": ["All"],
                "AttributeNames": ["All"],  # Include ApproximateReceiveCount
            }

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: client.receive_message(**receive_params)
            )

            messages = []
            malformed_messages = []

            for sqs_message in response.get("Messages", []):
                task_message = self._parse_sqs_message(sqs_message)
                if task_message:
                    messages.append(task_message)
                else:
                    malformed_messages.append(sqs_message["ReceiptHandle"])

            # Delete malformed messages
            for receipt_handle in malformed_messages:
                await self.delete_message(receipt_handle)

        except ClientError:
            logger.exception("Failed to receive messages:")
            return []
        except Exception:
            logger.exception("Unexpected error receiving messages:")
            return []
        else:
            return messages

    async def delete_message(self, receipt_handle: str) -> bool:
        """Delete a message from SQS queue."""
        try:
            client = await self._get_client()

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.delete_message(
                    QueueUrl=self.queue_url, ReceiptHandle=receipt_handle
                ),
            )

        except ClientError:
            logger.exception("Failed to delete message:")
            return False
        except Exception:
            logger.exception("Unexpected error deleting message:")
            return False
        else:
            return True

    async def change_message_visibility(self, receipt_handle: str, visibility_timeout: int) -> bool:
        """Change message visibility timeout."""
        try:
            client = await self._get_client()

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: client.change_message_visibility(
                    QueueUrl=self.queue_url,
                    ReceiptHandle=receipt_handle,
                    VisibilityTimeout=visibility_timeout,
                ),
            )

        except ClientError:
            logger.exception("Failed to change message visibility:")
            return False
        except Exception:
            logger.exception("Unexpected error changing message visibility:")
            return False
        else:
            return True

    async def get_queue_attributes(self) -> dict:
        """Get queue attributes."""
        try:
            client = await self._get_client()

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.get_queue_attributes(
                    QueueUrl=self.queue_url,
                    AttributeNames=[
                        "ApproximateNumberOfMessages",
                        "ApproximateNumberOfMessagesNotVisible",
                        "CreatedTimestamp",
                        "LastModifiedTimestamp",
                        "QueueArn",
                        "VisibilityTimeout",
                        "MessageRetentionPeriod",
                        "ReceiveMessageWaitTimeSeconds",
                    ],
                ),
            )

            return response.get("Attributes", {})  # type: ignore[no-any-return]

        except ClientError:
            logger.exception("Failed to get queue attributes:")
            return {}
        except Exception:
            logger.exception("Unexpected error getting queue attributes:")
            return {}
