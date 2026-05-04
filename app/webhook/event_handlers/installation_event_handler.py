from fastapi import HTTPException

from app.core.utils.constants import GitHubWHAction, QueueConstants
from app.webhook.logger import logger
from app.workers.embeddings_worker import create_repo_embeddings


class InstallationEventHandler:

    def handle(self, payload):
        action = payload.get("action")
        if action == GitHubWHAction.CREATED:
            self.on_created(payload)
        elif action == GitHubWHAction.DELETED:
            self.on_deleted(payload)

    @staticmethod
    def validate_payload(payload):
        installation = payload.get("installation", {})
        installation_id = installation.get("id")
        owner = installation.get("account", {}).get("login")
        repositories = payload.get("repositories", [])
        REQUIRED_FIELDS = [installation_id, owner, repositories]
        for field in REQUIRED_FIELDS:
            if not field:
                logger.error("Required field %s is missing in payload", field)
                raise HTTPException(
                    status_code=400,
                    detail=f"Required field {field} is missing in payload",
                )
        return installation_id, owner, repositories

    def on_created(self, payload):
        installation_id, owner, repositories = self.validate_payload(payload)
        repo_full_names = [repo.get("full_name") for repo in repositories]
        for repo in repo_full_names:
            task_id = f"{repo}_create_embeddings"
            create_repo_embeddings.apply_async(
                task_id=task_id,
                args=(installation_id, owner, repo),
                countdown=10,
                retry=True,
                queue=QueueConstants.CREATE_REPO_EMBEDDINGS_QUEUE
            )
            logger.info("Repo embedding creation pushed to queue task_id: %s", task_id)

    @staticmethod
    def on_deleted(payload):
        installation_id = payload.get("installation", {}).get("id")
        # TODO archive flow
