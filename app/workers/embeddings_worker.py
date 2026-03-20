from app.core.celery_app import celery_app
from app.core.services.embedding_service import EmbeddingService


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},
                 name="app.workers.embedding_worker.create_repo_embeddings")
def create_repo_embeddings(self, installation_id, owner, repo):
    print(f"[WORKER] Creating repo embeddings for owner: {owner} repo: {repo}") # TODO replace with logger
    embedding_service = EmbeddingService(installation_id=installation_id)
    embedding_service.create_repo_embeddings(owner, repo)
    print(f"[WORKER] Repo embeddings done PR for owner: {owner} repo: {repo}") # TODO replace with logger
