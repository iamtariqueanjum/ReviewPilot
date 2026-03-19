from app.core.celery_app import celery_app
from app.core.services.review_service import ReviewService


@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},
                 name="app.workers.review_worker.review_pr")
def review_pr(installation_id, owner, repo, pr_number, head_sha):
    print(f"[WORKER] Reviewing PR {repo}#{pr_number}") # TODO replace with logger
    review_service = ReviewService(installation_id=installation_id)
    response = review_service.review_pr(
        owner=owner, repo=repo, pr_number=pr_number, head_sha=head_sha
    )
    print(f"[WORKER] Review done PR {repo}#{pr_number}") # TODO replace with logger
    return response
