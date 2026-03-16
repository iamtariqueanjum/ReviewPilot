import logging

from app.llm.llm_factory import LLMFactory
from app.prompts.review_pr.final_prompt import prompt
from app.services.github_service import GithubService


logging = logging.getLogger(__name__)


class ReviewService(object):

    def __init__(self, installation_id, provider=None):
        self.installation_id = installation_id
        self.github_service = GithubService(installation_id)
        self.llm = LLMFactory.get_llm(provider)
        self.chain = prompt | self.llm


    def get_pr_diff(self, owner, repo, pr_number):
        try:
            files = self.github_service.get_pr_files(owner, repo, pr_number)
            diff = ""
            for file in files:
                filename = file.get("filename")
                patch = file.get("patch")
                status = file.get("status")
                diff += f"File: {filename}\nStatus: {status}\nPatch:\n{patch}\n\n"
            return diff
        except Exception as e:
            logging.exception(f"Error while fetching PR diff for {owner}/{repo}#{pr_number}")
            raise ValueError(f"Error while fetching PR diff for {owner}/{repo}#{pr_number}: {str(e)}")


    def review_pr(self, owner, repo, pr_number):
        pr_diff = self.get_pr_diff(owner, repo, pr_number)
        print(f"PR Diff for {owner}/{repo}#{pr_number}:\n{pr_diff}\n")
        response = self.chain.invoke(
            {"pr_diff": pr_diff}
        )
        print(f"LLM response for PR review:\n{response}\n")
        # TODO call GitHub API to post the review comments/suggestions on the PR using the GithubService