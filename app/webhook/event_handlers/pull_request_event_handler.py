from app.utils.constants import GitHubWHAction


class PullRequestEventHandler(object):

    def handle(self, payload):
        action = payload.get("action")
        owner = payload.get("repository", {}).get("owner", {}).get("login")
        repo = payload.get("repository").get("name")
        pr = payload.get("pull_request", {})
        pr_number = pr.get("number")

        if action == GitHubWHAction.OPENED:
            self.on_opened(owner, repo, pr_number)
        elif action == GitHubWHAction.SYNCHRONIZE:
            self.on_synchronize(owner, repo, pr_number)
        elif action == GitHubWHAction.REOPENED:
            self.on_reopened(owner, repo, pr_number)
        elif action == GitHubWHAction.CLOSED:
            self.on_closed(owner, repo, pr_number, payload)

    @staticmethod
    def on_opened(owner, repo, pr_number):
        # TODO call AI review for the PR
        print(f"Pull request has been opened... Pr is being reviewed...\n")
        # review_service.review_pr(owner, repo, pr_number)

    @staticmethod
    def on_synchronize(owner, repo, pr_number):
        # TODO call re-review for the PR changes
        print(f"Pull request has been synced... Pr is being re-reviewed\n")
        # review_service.review_pr(owner, repo, pr_number, re_review=True)

    @staticmethod
    def on_reopened(owner, repo, pr_number):
        # TODO call AI review for the PR
        print(f"Pull request has been reopened... Pr is being reviewed again...\n")
        # review_service.review_pr(owner, repo, pr_number)

    @staticmethod
    def on_closed(owner, repo, pr_number, payload):
        # TODO update repo embeddings with the new changes from the merged PR
        if payload.get("pull_request", {}).get("merged"):
            print(f"Pull request has been merged... Updating repo embeddings....\n")
            # embedding_service.update_repo_embeddings(owner, repo)