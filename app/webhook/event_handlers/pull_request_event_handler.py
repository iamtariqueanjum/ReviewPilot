from app.core.api.client import APIClient
from app.core.utils.constants import GitHubWHAction, APIEndpoints, HTTPMethod, QueueConstants
from app.workers.review_worker import review_pr


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
        REQUIRED_FIELDS = [owner, repo, pr_number, head_sha, installation_id]
        for field in REQUIRED_FIELDS:
            if not field:
                print(f"Required field {field} not found in payload\n")
                return {"error": f"Required field {field} not found in payload", "status": "error"}
        review_id = f"{repo}_{pr_number}_{head_sha}"
        review_pr.apply_async(
            task_id=review_id,
            args=(installation_id, owner, repo, pr_number, head_sha),
            countdown=10,
            retry=True,
            queue=QueueConstants.REVIEW_PR_QUEUE
        )
        print(f"Review pushed to queue {review_id}\n")
        # response = self.api_client.call_api(
        #     method=HTTPMethod.POST,
        #     path=APIEndpoints.REVIEW_PR.value,
        #     json={"owner": owner, "repo": repo, "pr_number": pr_number, "head_sha": head_sha,
        #           "installation_id": installation_id}
        # )
        return {"message": f"Review for PR {owner}/{repo}#{pr_number} has been queued", "status": "success"}

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