from app.clients.api_client import APIClient
from app.utils.constants import GitHubWHAction, APIEndpoints, HTTPMethod


class PullRequestEventHandler(object):

    def __init__(self):
        self.api_client = APIClient()
        self.embedding_service = None  # TODO initialize embedding service

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

    def on_opened(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        installation_id = payload.get("installation", {}).get("id")
        response = self.api_client.call_api(
            method=HTTPMethod.POST,
            path=APIEndpoints.REVIEW_PR.value,
            json={"owner": owner, "repo": repo, "pr_number": pr_number, "installation_id": installation_id}
        )

    def on_synchronize(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        installation_id = payload.get("installation", {}).get("id")
        response = self.api_client.call_api(
            method=HTTPMethod.POST,
            path=APIEndpoints.REVIEW_PR.value,
            json={"owner": owner, "repo": repo, "pr_number": pr_number, "installation_id": installation_id,
                  "re_review": True}
        )

    def on_reopened(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        installation_id = payload.get("installation", {}).get("id")
        response = self.api_client.call_api(
            method=HTTPMethod.POST,
            path=APIEndpoints.REVIEW_PR.value,
            json={"owner": owner, "repo": repo, "pr_number": pr_number, "installation_id": installation_id,
                  "re_review": True}
        )

    def on_closed(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        if payload.get("pull_request", {}).get("merged"):
            # TODO update repo embeddings with the new changes from the merged PR
            print(f"Pull request has been merged... Updating repo embeddings....\n")
            self.embedding_service.update_repo_embeddings(owner, repo)