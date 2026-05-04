from fastapi import HTTPException

from app.core.api.client import APIClient
from app.core.utils.constants import GitHubWHAction, QueueConstants
from app.webhook.logger import logger
from app.workers.review_worker import review_pr


class PullRequestEventHandler:

    def __init__(self):
        self.api_client = APIClient()
        # self.embedding_service = None

    def handle(self, payload):
        action = payload.get("action")

        if action == GitHubWHAction.OPENED:
            self.on_opened(payload)
        elif action == GitHubWHAction.SYNCHRONIZE:
            self.on_synchronize(payload)
        elif action == GitHubWHAction.REOPENED:
            self.on_reopened(payload)
        elif action == GitHubWHAction.CLOSED:
            self.on_closed(payload)

    @staticmethod
    def validate_payload(payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        head_sha = pr.get("head", {}).get("sha")
        installation_id = payload.get("installation", {}).get("id")
        REQUIRED_FIELDS = [installation_id, owner, repo, pr_number, head_sha]
        for field in REQUIRED_FIELDS:
            if not field:
                logger.error("Required field %s is missing in payload", field)
                raise HTTPException(
                    status_code=400,
                    detail=f"Required field {field} is missing in payload",
                )
        return installation_id, owner, repo, pr_number, head_sha

    def on_opened(self, payload):
        installation_id, owner, repo, pr_number, head_sha  = self.validate_payload(payload)
        review_id = f"{repo}_{pr_number}_{head_sha}"
        review_pr.apply_async(
            task_id=review_id,
            args=(installation_id, owner, repo, pr_number, head_sha),
            countdown=10,
            retry=True,
            queue=QueueConstants.REVIEW_PR_QUEUE
        )
        logger.info("Review pushed to queue review_id: %s", review_id)

    def on_synchronize(self, payload):
        installation_id, owner, repo, pr_number, head_sha = self.validate_payload(payload)
        logger.info("Synchronize event received for PR %s#%s with head SHA %s", repo, pr_number, head_sha)
        # TODO re-review diff only instead of whole pr

    def on_reopened(self, payload):
        installation_id, owner, repo, pr_number, head_sha = self.validate_payload(payload)
        review_id = f"{repo}_{pr_number}_{head_sha}"
        review_pr.apply_async(
            task_id=review_id,
            args=(installation_id, owner, repo, pr_number, head_sha),
            countdown=10,
            retry=True,
            queue=QueueConstants.REVIEW_PR_QUEUE
        )
        logger.info("Review pushed to queue review_id: %s", review_id)

    def on_closed(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        if payload.get("pull_request", {}).get("merged"):
            # TODO update repo embeddings with the new changes from the merged PR
            logger.info("Pull request merged owner: %s repo : %s", owner, repo)
            logger.info("Updating repo embeddings : %s", owner, repo)
            # self.embedding_service.update_repo_embeddings(owner, repo)
