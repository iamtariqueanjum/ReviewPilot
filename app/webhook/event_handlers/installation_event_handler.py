from app.core.utils.constants import GitHubWHAction, QueueConstants
from app.workers.embeddings_worker import create_repo_embeddings


class InstallationEventHandler(object):

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
                print(f"Required field {field} not found in payload\n")
                return False, f"Required field {field} not found in payload"  # TODO raise 400
        return installation_id, owner, repositories

    def on_created(self, payload):
        installation_id, owner, repositories = self.validate_payload(payload)
        repo_full_names = [repo.get("full_name") for repo in repositories]
        print(f"Repositories: {repo_full_names}\n")
        print(f"Creating repo embeddings for the repositories....\n")
        for repo in repo_full_names:
            task_id = f"{repo}_create_embeddings" # TODO generate unique task_id for the repo embeddings creation task
            create_repo_embeddings.apply_async(
                task_id=task_id,
                args=(installation_id, owner, repo),
                countdown=10,
                retry=True,
                queue=QueueConstants.CREATE_REPO_EMBEDDINGS_QUEUE
            )
            print(f"Repo embedding creation pushed to queue {task_id}\n")
        # TODO Embedding Service call to create repo embeddings for all repos in the installation

    @staticmethod
    def on_deleted(payload):
        print(f"Destroyed installation with ID: {payload.get('installation', {}).get('id')}")
        print(f"Deleting repo embeddings for the repositories...\n")