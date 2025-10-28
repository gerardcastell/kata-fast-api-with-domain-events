import asyncio
import contextlib
import logging
import signal
import time

from app.shared.infrastructure.sqs.client import SQSClient
from app.shared.infrastructure.sqs.models import TaskMessage, TaskResult, TaskStatus, WorkerConfig

logger = logging.getLogger(__name__)


class TaskProcessor:
    """Base class for task processors."""

    def __init__(self, task_type: str):
        self.task_type = task_type

    async def process(self, message: TaskMessage) -> TaskResult:
        """Process a task message."""
        raise NotImplementedError("Subclasses must implement process method")


class SQSWorker:
    """SQS worker for processing async tasks."""

    def __init__(
        self,
        sqs_client: SQSClient,
        config: WorkerConfig | None = None,
    ):
        self.sqs_client = sqs_client
        self.config = config or WorkerConfig()
        self.processors: dict[str, TaskProcessor] = {}
        self.running = False
        self.shutdown_event = asyncio.Event()
        self.active_tasks: dict[str, asyncio.Task] = {}

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum, _frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            loop = asyncio.get_event_loop()
            _shutdown_task = loop.create_task(self.stop())  # noqa: RUF006

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def register_processor(self, processor: TaskProcessor):
        """Register a task processor."""
        self.processors[processor.task_type] = processor
        logger.info(f"Registered processor for task type: {processor.task_type}")

    async def start(self):
        """Start the worker."""
        if self.running:
            logger.warning("Worker is already running")
            return

        logger.info("Starting SQS worker...")
        self.running = True
        self.shutdown_event.clear()

        try:
            # Start health check task
            health_task = asyncio.create_task(self._health_check())

            # Start main processing loop
            await self._process_loop()

            # Wait for health check to complete
            health_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await health_task

        except Exception:
            logger.exception("Worker error")
        finally:
            self.running = False
            logger.info("SQS worker stopped")

    async def stop(self):
        """Stop the worker gracefully."""
        if not self.running:
            return

        logger.info("Stopping SQS worker...")
        self.running = False
        self.shutdown_event.set()

        # Wait for active tasks to complete
        if self.active_tasks:
            logger.info(f"Waiting for {len(self.active_tasks)} active tasks to complete...")
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self.active_tasks.values(), return_exceptions=True),
                    timeout=self.config.shutdown_timeout_seconds,
                )
            except asyncio.TimeoutError:
                logger.warning("Timeout waiting for active tasks to complete")
                # Cancel remaining tasks
                for task in self.active_tasks.values():
                    if not task.done():
                        task.cancel()

        logger.info("SQS worker stopped gracefully")

    async def _process_loop(self):
        """Main processing loop."""
        while self.running and not self.shutdown_event.is_set():
            try:
                # Check if we can process more tasks
                if len(self.active_tasks) >= self.config.max_concurrent_tasks:
                    await asyncio.sleep(self.config.poll_interval_seconds)
                    continue

                # Receive messages from SQS
                messages = await self.sqs_client.receive_messages()

                if not messages:
                    await asyncio.sleep(self.config.poll_interval_seconds)
                    continue

                # Process messages concurrently
                for message in messages:
                    if len(self.active_tasks) >= self.config.max_concurrent_tasks:
                        break

                    task = asyncio.create_task(self._process_message(message))
                    self.active_tasks[str(message.task_id)] = task

            except Exception:
                logger.exception("Error in process loop")
                await asyncio.sleep(self.config.poll_interval_seconds)

    async def _process_message(self, message: TaskMessage):
        """Process a single message."""
        task_id = str(message.task_id)
        start_time = time.time()

        try:
            logger.info(f"Processing task {task_id} of type {message.task_type}")

            # Get processor for this task type
            processor = self.processors.get(message.task_type)
            if not processor:
                logger.error(f"No processor found for task type: {message.task_type}")
                await self._handle_task_failure(message, "No processor found")
                return

            # Process the task
            result = await processor.process(message)

            # Handle successful completion
            if result.status == TaskStatus.COMPLETED:
                await self._handle_task_success(message, result)
            else:
                await self._handle_task_failure(message, result.error_message)  # type: ignore[arg-type]

        except Exception as e:
            logger.exception(f"Error processing task {task_id}")
            await self._handle_task_failure(message, str(e))
        finally:
            # Remove from active tasks
            self.active_tasks.pop(task_id, None)

            processing_time = time.time() - start_time
            logger.info(f"Task {task_id} completed in {processing_time:.2f} seconds")

    async def _handle_task_success(self, message: TaskMessage, result: TaskResult):
        """Handle successful task completion."""
        try:
            # Delete message from SQS
            if hasattr(message, "_receipt_handle"):
                await self.sqs_client.delete_message(message._receipt_handle)

            logger.info(f"Task {message.task_id} completed successfully. Result: {result}")

        except Exception:
            logger.exception("Error handling task success")

    async def _handle_task_failure(self, message: TaskMessage, error_message: str):
        """Handle task failure."""
        try:
            # Check if we should retry
            if message.retry_count < message.max_retries:
                # Increment retry count and resend message
                message.retry_count += 1
                message.delay_seconds = min(
                    60 * (2**message.retry_count), 900
                )  # Exponential backoff

                await self.sqs_client.send_message(message)
                logger.info(
                    f"Task {message.task_id} failed, retrying ({message.retry_count}/{message.max_retries})"
                )
            else:
                # Max retries exceeded, delete message
                if hasattr(message, "_receipt_handle"):
                    await self.sqs_client.delete_message(message._receipt_handle)
                logger.error(
                    f"Task {message.task_id} failed permanently after {message.max_retries} retries. Error message: {error_message}"
                )

        except Exception:
            logger.exception("Error handling task failure")

    async def _health_check(self):
        """Periodic health check."""
        while self.running and not self.shutdown_event.is_set():
            try:
                await asyncio.sleep(self.config.health_check_interval_seconds)

                # Get queue attributes
                attributes = await self.sqs_client.get_queue_attributes()

                logger.info(
                    f"Worker health check - Active tasks: {len(self.active_tasks)}, "
                    f"Queue messages: {attributes.get('ApproximateNumberOfMessages', 'N/A')}"
                )

            except Exception:  # noqa: PERF203
                logger.exception("Health check error")
