from celery import Celery

from app.config.settings import settings

app = Celery("celery_app")

app.conf.update(
    broker_url=f"sqs://{settings.AWS_ACCESS_KEY_ID}:{settings.AWS_SECRET_ACCESS_KEY}@localstack:4566/",
    broker_transport="sqs",
    broker_transport_options={
        "region": settings.AWS_REGION,
        "predefined_queues": {
            settings.SQS_QUEUE: {
                "url": settings.SQS_QUEUE_URL,
                "access_key_id": settings.AWS_ACCESS_KEY_ID,
                "secret_access_key": settings.AWS_SECRET_ACCESS_KEY,
                
            }
        },
        "visibility_timeout": 10,
    },
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_queue=settings.SQS_QUEUE,
    task_default_exchange_type="direct",
)


# Example task for testing
@app.task(bind=True)
def unstable_task(self, x):
    print("Processing task")
    if x < 0:
        raise ValueError("Intentional failure to test DLQ")
    return x * 2
