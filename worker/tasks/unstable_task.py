from worker.celery import app
from celery.exceptions import Reject


@app.task(bind=True, name="tasks.unstable_task", queue="default", acks_late=True)
def unstable_task(self, x):
    print("Processing task:", x)
    if x < 0:
        # Send straight to DLQ
        raise Reject("Intentional failure", requeue=False)
    return x * 2
