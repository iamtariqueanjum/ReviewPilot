from celery import Celery

from app.core.utils.constants import ConfigConstants

celery_app = Celery(
    "review_pilot",
    broker=ConfigConstants.CELERY_BROKER_URL,
    backend=ConfigConstants.CELERY_BACKEND_URL,
)

celery_app.conf.task_routes = {
    "app.tasks.review_tasks.review_pr_task": {"queue": "review_queue"},
}
