from app.core.utils.constants import GitHubWHAction


class InstallationEventHandler(object):

    def handle(self, payload):
        action = payload.get("action")

        if action == GitHubWHAction.CREATED:
            self.on_created(payload)
        elif action == GitHubWHAction.DELETED:
            self.on_deleted(payload)

    @staticmethod
    def on_created(payload):
        installation = payload.get("installation", {})
        installation_id = installation.get("id")

        print(f"Installation ID: {installation_id}")
        if not installation_id:
            return {"error": "Installation ID not found in payload", "status": "error"}
        repositories = payload.get("repositories")
        repo_full_names = [repo.get("full_name") for repo in repositories]
        print(f"Repositories: {repo_full_names}\n")
        print(f"Creating repo embeddings for the repositories....\n")
        # TODO Embedding Service call to create repo embeddings for all repos in the installation

    @staticmethod
    def on_deleted(payload):
        print(f"Destroyed installation with ID: {payload.get('installation', {}).get('id')}")
        print(f"Deleting repo embeddings for the repositories...\n")