from app.core.celery_app import celery_app
from app.core.services.embedding_service import EmbeddingService


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},
                 name="app.workers.embedding_worker.create_repo_embeddings")
def create_repo_embeddings(self, repo):
    print(f"[WORKER] Creating repo embeddings for repo: {repo}") # TODO replace with logger
    embedding_service = EmbeddingService()
    embedding_service.create_repo_embeddings(repo)
    print(f"[WORKER] Repo embeddings done PR for repo: {repo}") # TODO replace with logger
