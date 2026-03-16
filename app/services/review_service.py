from app.services.github_service import GithubService
from app.llm.llm_factory import LLMFactory


class ReviewService(object):

    def __init__(self, installation_id, provider=None):
        self.installation_id = installation_id
        self.github_service = GithubService(installation_id)
        self.llm = LLMFactory.get_llm(provider)



    def review_pr(self, owner, repo, pr_number):
        print(f"Reviewing PR {owner}/{repo}#{pr_number}...\n")
        # TODO call GitHub API to fetch PR details and files changed in the PR using the GithubService
        # TODO call AI review module to review the PR and get the review comments/suggestions
        # TODO call GitHub API to post the review comments/suggestions on the PR using the GithubService
        pass
