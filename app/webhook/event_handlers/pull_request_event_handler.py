from app.core.api.client import APIClient
from app.utils.constants import GitHubWHAction, APIEndpoints, HTTPMethod


class PullRequestEventHandler(object):

    def __init__(self):
        self.api_client = APIClient()
        self.embedding_service = None  # TODO initialize embedding service

    def handle(self, payload):
        action = payload.get("action")
        print(f"Handling pull request event with action: {action}\n")
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
        head_sha = pr.get("head", {}).get("sha")
        print(f"Open event received for PR {owner}/{repo}#{pr_number} with head SHA {head_sha}\n")
        installation_id = payload.get("installation", {}).get("id")
        response = self.api_client.call_api(
            method=HTTPMethod.POST,
            path=APIEndpoints.REVIEW_PR.value,
            json={"owner": owner, "repo": repo, "pr_number": pr_number, "head_sha": head_sha,
                  "installation_id": installation_id}
        )
        print(f"API Call made - Review response: {response}\n")

    def on_synchronize(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        head_sha = pr.get("head", {}).get("sha")
        print(f"Synchronize event received for PR {owner}/{repo}#{pr_number} with head SHA {head_sha}\n")
        installation_id = payload.get("installation", {}).get("id")
        response = self.api_client.call_api(
            method=HTTPMethod.POST,
            path=APIEndpoints.REVIEW_PR.value,
            json={"owner": owner, "repo": repo, "pr_number": pr_number, "head_sha": head_sha,
                  "installation_id": installation_id, "re_review": True}
        )
        print(f"API Call made - Review response: {response}\n")

    def on_reopened(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")
        head_sha = pr.get("head", {}).get("sha")
        print(f"Re-open event received for PR {owner}/{repo}#{pr_number} with head SHA {head_sha}\n")
        installation_id = payload.get("installation", {}).get("id")
        response = self.api_client.call_api(
            method=HTTPMethod.POST,
            path=APIEndpoints.REVIEW_PR.value,
            json={"owner": owner, "repo": repo, "pr_number": pr_number, "head_sha": head_sha,
                  "installation_id": installation_id, "re_review": True}
        )
        print(f"API Call made - Review response: {response}\n")

    def on_closed(self, payload):
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        if payload.get("pull_request", {}).get("merged"):
            # TODO update repo embeddings with the new changes from the merged PR
            print(f"Pull request has been merged... Updating repo embeddings....\n")
            self.embedding_service.update_repo_embeddings(owner, repo)