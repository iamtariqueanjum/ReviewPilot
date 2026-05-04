from app.core.celery_app import celery_app
from app.core.services.review_service import ReviewService
from app.workers.logger import logger

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=5, retry_kwargs={"max_retries": 3},
                 name="app.workers.review_worker.review_pr")
def review_pr(self, installation_id, owner, repo, pr_number, head_sha):
    logger.info("Reviewing PR %s#%s", repo, pr_number)
    review_service = ReviewService(
        owner, repo, installation_id
    )
    response = review_service.review_pr(
        pr_number=pr_number, head_sha=head_sha
    )
    logger.info("Review done PR %s#%s", repo, pr_number)
    return response
