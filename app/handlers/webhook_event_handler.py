from app.utils.constants import GitHubWHAction, GitHubWHEvent


class WebhookEventHandler(object):

    @staticmethod
    def handle_event(event, payload):
        if event == GitHubWHEvent.INSTALLATION and payload.get("action") == GitHubWHAction.CREATED:
            installation = payload.get("installation")
            installation_id = installation.get("id")
            print(f"Installation ID: {installation_id}")
            if not installation_id:
                return {"error": "Installation ID not found in payload", "status": "error"}
            repositories = payload.get("repositories")
            repo_full_names = [repo.get("full_name") for repo in repositories]
            print(f"Repositories: {repo_full_names}\n")
            # TODO Embedding Service call to create repo embeddings for all repos in the installation
        elif event == GitHubWHEvent.PULL_REQUEST:
            action = payload.get("action")
            if action == GitHubWHAction.OPENED:
                # TODO call AI review for the PR
                pass
            elif action == GitHubWHAction.SYNCHRONIZE:
                # TODO call re-review for the PR changes
                pass
            elif action == GitHubWHAction.CLOSED and payload.get("pull_request", {}).get("merged"):
                # TODO update repo embeddings with the new changes from the merged PR
                pass
        elif event == GitHubWHEvent.PUSH:
            # TODO update repo embeddings with the new changes from the push
            pass
