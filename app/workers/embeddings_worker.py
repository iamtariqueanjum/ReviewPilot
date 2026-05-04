from app.core.celery_app import celery_app
from app.core.services.embedding_service import EmbeddingService
from app.workers.logger import logger


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},
                 name="app.workers.embedding_worker.create_repo_embeddings")
def create_repo_embeddings(self, installation_id, owner, repo):
    logger.info("Creating repo embeddings for owner: %s repo: %s", owner, repo)
    embedding_service = EmbeddingService(owner, repo, installation_id)
    embedding_service.create_repo_embeddings()
    logger.info("Created repo embeddings for owner: %s repo: %s", owner, repo)
