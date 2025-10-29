from typing import Any

from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException

from app.shared.containers.main import Container
from app.shared.infrastructure.sqs.models import TaskPriority

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskRequest(BaseModel):
    task_type: str
    payload: dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    delay_seconds: int = 0


class BatchTaskRequest(BaseModel):
    tasks: list[tuple[str, dict[str, Any]]]
    priority: TaskPriority = TaskPriority.NORMAL
    delay_seconds: int = 0


class TaskResponse(BaseModel):
    task_id: str | None
    success: bool
    message: str


class BatchTaskResponse(BaseModel):
    task_ids: list[str]
    success_count: int
    total_count: int


@router.post("/dispatch", response_model=TaskResponse)
async def dispatch_task(
    request: TaskRequest,
    container: Container = Depends(),
):
    """Dispatch a single task to SQS."""
    try:
        dispatcher = container.task_dispatcher()
        task_id = await dispatcher.dispatch_task(
            task_type=request.task_type,
            payload=request.payload,
            priority=request.priority,
            delay_seconds=request.delay_seconds,
        )

        if task_id:
            return TaskResponse(
                task_id=task_id,
                success=True,
                message="Task dispatched successfully",
            )
        else:
            return TaskResponse(
                task_id=None,
                success=False,
                message="Failed to dispatch task",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dispatch-batch", response_model=BatchTaskResponse)
async def dispatch_batch_tasks(
    request: BatchTaskRequest,
    container: Container = Depends(),
):
    """Dispatch multiple tasks to SQS."""
    try:
        dispatcher = container.task_dispatcher()
        task_ids = await dispatcher.dispatch_batch_tasks(
            tasks=request.tasks,
            priority=request.priority,
            delay_seconds=request.delay_seconds,
        )

        return BatchTaskResponse(
            task_ids=task_ids,
            success_count=len(task_ids),
            total_count=len(request.tasks),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue-status")
async def get_queue_status(container: Container = Depends()):
    """Get SQS queue status and attributes."""
    try:
        sqs_client = container.sqs_client()
        attributes = await sqs_client.get_queue_attributes()

        return {
            "queue_url": sqs_client.queue_url,
            "approximate_number_of_messages": attributes.get("ApproximateNumberOfMessages", "0"),
            "approximate_number_of_messages_not_visible": attributes.get(
                "ApproximateNumberOfMessagesNotVisible", "0"
            ),
            "approximate_number_of_messages_delayed": attributes.get(
                "ApproximateNumberOfMessagesDelayed", "0"
            ),
            "visibility_timeout": attributes.get("VisibilityTimeout", "0"),
            "message_retention_period": attributes.get("MessageRetentionPeriod", "0"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Example endpoints for common task types
@router.post("/data-processing", response_model=TaskResponse)
async def dispatch_data_processing_task(
    data: list,
    processing_type: str = "default",
    container: Container = Depends(),
):
    """Dispatch a data processing task."""
    request = TaskRequest(
        task_type="data_processing",
        payload={"data": data, "processing_type": processing_type},
    )
    return await dispatch_task(request, container)


@router.post("/email-notification", response_model=TaskResponse)
async def dispatch_email_notification_task(
    recipient: str,
    subject: str,
    body: str = "",
    template: str | None = None,
    container: Container = Depends(),
):
    """Dispatch an email notification task."""
    request = TaskRequest(
        task_type="email_notification",
        payload={
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "template": template,
        },
    )
    return await dispatch_task(request, container)


@router.post("/report-generation", response_model=TaskResponse)
async def dispatch_report_generation_task(
    report_type: str,
    date_range: dict[str, str],
    format_type: str = "pdf",
    container: Container = Depends(),
):
    """Dispatch a report generation task."""
    request = TaskRequest(
        task_type="report_generation",
        payload={
            "report_type": report_type,
            "date_range": date_range,
            "format": format_type,
        },
    )
    return await dispatch_task(request, container)
