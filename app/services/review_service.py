from app.services.github_service import GithubService


class ReviewService(object):

    def __init__(self, installation_id):
        self.installation_id = installation_id
        self.github_service = GithubService(installation_id)


    def review_pr(self, owner, repo, pr_number):
        print(f"Reviewing PR {owner}/{repo}#{pr_number}...\n")
        # TODO call GitHub API to fetch PR details and files changed in the PR using the GithubService
        # TODO call AI review module to review the PR and get the review comments/suggestions
        # TODO call GitHub API to post the review comments/suggestions on the PR using the GithubService
        pass
