import os
from celery import Celery

broker_url = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://redis:6379/0"))
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

celery_app = Celery(
    "diffrun",
    broker=broker_url,
    backend=result_backend,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.tasks.generate_page": {"queue": "gpu"},
        "app.tasks.regenerate_page": {"queue": "gpu"},
    },
)