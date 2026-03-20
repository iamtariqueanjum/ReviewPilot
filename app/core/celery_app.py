from celery import Celery

from app.core.utils.constants import ConfigConstants, QueueConstants

celery_app = Celery(
    "review_pilot",
    broker=ConfigConstants.CELERY_BROKER_URL,
    backend=ConfigConstants.CELERY_BACKEND_URL,
)

celery_app.conf.task_routes = {
    "app.workers.review_worker.review_pr": {"queue": QueueConstants.REVIEW_PR_QUEUE},
    "app.workers.embedding_worker.create_repo_embeddings": {"queue": QueueConstants.CREATE_REPO_EMBEDDINGS_QUEUE},
}
celery_app.autodiscover_tasks(["app.workers"])
import app.workers.review_worker
import app.workers.embeddings_worker