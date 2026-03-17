import logging
import re

from app.api.models.review_response import ReviewLLMResponse
from app.llm.llm_factory import LLMFactory
from app.prompts.review_pr.final_prompt import prompt
from app.services.github_service import GithubService


logging = logging.getLogger(__name__)


class ReviewService(object):

    def __init__(self, installation_id, provider=None):
        self.installation_id = installation_id
        self.github_service = GithubService(installation_id)
        self.llm = LLMFactory.get_llm(provider)
        self.structured_llm = self.llm.with_structured_output(ReviewLLMResponse)
        self.chain = prompt | self.structured_llm

    def get_pr_diff(self, owner, repo, pr_number, head_sha):
        try:
            files = self.github_service.get_pr_files(owner, repo, pr_number)
            diff = ""
            for file in files:
                file_path = file.get("filename")
                patch = file.get("patch")
                if not patch:
                    continue
                changed_lines = self.parse_new_lines(patch)
                # TODO too many api calls if there are many files
                file_lines = self.github_service.get_file_content(owner, repo, file_path, head_sha).split('\n')
                if not file_lines:
                    continue
                for line in changed_lines:
                    approx_line = line.get("line")
                    target = line.get("content")
                    line["line"] = self.get_new_file_line_number(file_lines, target, approx_line)
                status = file.get("status")
                diff += f"File: {file_path}\nStatus: {status}\nChanged lines:\n{changed_lines}\n\n"
            return diff
        except Exception as e:
            logging.exception(f"Error while fetching PR diff for {owner}/{repo}#{pr_number}")
            raise ValueError(f"Error while fetching PR diff for {owner}/{repo}#{pr_number}: {str(e)}")


    def review_pr(self, owner, repo, pr_number, head_sha):
        # TODO exception handling
        pr_diff = self.get_pr_diff(owner, repo, pr_number, head_sha)
        print(f"PR Diff for {owner}/{repo}#{pr_number}:\n{pr_diff}\n")
        # TODO exception handling
        response = self.chain.invoke(
            {"pr_diff": pr_diff}
        )
        print(f"LLM response for PR review:\n{response}\n")
        # TODO call GitHub API to post the review comments/suggestions on the PR using the GithubService

    @staticmethod
    def parse_new_lines(patch):
        changes = []
        new_line = 0
        for line in patch.split("\n"):
            if not line.strip():
                continue
            # Extract the new line number from the hunk header
            if line.startswith("@@"):
                match = re.search(r"\+(\d+)", line)
                if match:
                    new_line = int(match.group(1)) - 1
            # Added line
            elif line.startswith("+") and not line.startswith("+++"):
                new_line += 1
                changes.append({"line" :new_line, "content": line[1:]})
            # Removed line
            elif not line.startswith("-") and not line.startswith("---"):
                continue
            # Context line
            else:
                new_line += 1
        return changes

    @staticmethod
    def get_new_file_line_number(file_lines, target, approx_line):
        n = len(file_lines)
        target = target.strip()

        approx_line = min(max(approx_line, 1), len(file_lines))

        for i in range(approx_line - 1, n):
            if file_lines[i].strip() == target:
                return i + 1

        for i in range(approx_line - 2, -1, -1):
            if file_lines[i].strip() == target:
                return i + 1

        return approx_line
