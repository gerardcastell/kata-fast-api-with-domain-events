from celery import Celery
from kombu import Exchange, Queue

from celery import bootsteps

default_queue_name = 'default'
default_exchange_name = 'default'
default_routing_key = 'default'
deadletter_suffix = 'deadletter'
deadletter_queue_name = default_queue_name + f'.{deadletter_suffix}'
deadletter_exchange_name = default_exchange_name + f'.{deadletter_suffix}'
deadletter_routing_key = default_routing_key + f'.{deadletter_suffix}'


class DeclareDLXnDLQ(bootsteps.StartStopStep):
    """
    Celery Bootstep to declare the DL exchange and queues before the worker starts
        processing tasks
    """
    requires = {'celery.worker.components:Pool'}

    def start(self, worker):
        app = worker.app

        # Declare DLX and DLQ
        dlx = Exchange(deadletter_exchange_name, type='direct')

        dead_letter_queue = Queue(
            deadletter_queue_name, dlx, routing_key=deadletter_routing_key)

        with worker.app.pool.acquire() as conn:
            dead_letter_queue.bind(conn).declare()



app = Celery(
    "worker",
    broker="pyamqp://guest:guest@rabbitmq:5672//",
    backend=None,
)

default_exchange = Exchange(default_exchange_name, type='direct')
default_queue = Queue(
    default_queue_name,
    default_exchange,
    routing_key=default_routing_key,
    queue_arguments={
        'x-dead-letter-exchange': deadletter_exchange_name,
        'x-dead-letter-routing-key': deadletter_routing_key
    })

app.conf.task_queues = (default_queue, )

# Add steps to workers that declare DLX and DLQ if they don't exist
app.steps['worker'].add(DeclareDLXnDLQ)

app.conf.task_default_queue = default_queue_name
app.conf.task_default_exchange = default_exchange_name
app.conf.task_default_routing_key = default_routing_key

# Failed task handling
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True
app.conf.task_acks_on_failure_or_timeout = False

# Task routing (optional, ensures specific tasks go to main queue)
app.conf.task_routes = {
    "tasks.unstable_task": {"queue": "tasks.main"},
}

# Import tasks so they get registered
import worker.tasks.unstable_task