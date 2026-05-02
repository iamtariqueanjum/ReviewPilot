from app.core.logger import logger
from app.core.utils.diff_parser import parse_new_lines, get_new_file_line_number, prepare_changed_lines_text
from app.integrations.github.client import GitHubClient
from app.integrations.github.pr_service import PrService
from app.integrations.github.repo_service import RepoService
from app.integrations.github.comment_service import CommentService


class GithubService(object):

    def __init__(self, owner, repo, installation_id):
        self.owner = owner
        self.repo = repo
        self.client = GitHubClient(installation_id)
        self.pr_service = PrService(self.owner, self.repo, self.client)
        self.repo_service = RepoService(self.owner, self.repo, self.client)
        self.comment_service = CommentService(self.owner, self.repo, self.client)

    def get_pr(self, pr_number):
        return self.pr_service.get_pr(pr_number)

    def get_pr_files(self, pr_number):
        return self.pr_service.get_pr_files(pr_number)

    def get_repository(self):
        return self.repo_service.get_repository()

    def get_branch(self, branch):
        return self.repo_service.get_branch(branch)

    def get_tree_recursive(self, tree_sha):
        return self.repo_service.get_tree_recursive(tree_sha)

    def get_file_content(self, path, head_sha):
        return self.repo_service.get_file_content(path, head_sha)

    def get_blob_content(self, file_sha):
        return self.repo_service.get_blob_content(file_sha)

    def post_comment(self, issue_number, comment):
        return self.comment_service.post_comment(issue_number, comment)

    def get_pr_filepaths(self, pr_number):
        filepaths = []
        try:
            files = self.get_pr_files(pr_number)
            for file in files:
                filepaths.append(file.get("filename"))
            return filepaths
        except Exception as e:
            logger.exception(f"Error while fetching PR file paths for {self.owner}/{self.repo}#{pr_number}")
            raise ValueError(f"Error while fetching PR file paths for {self.owner}/{self.repo}#{pr_number}: {str(e)}")

    def get_pr_diff(self, pr_number, head_sha):
        try:
            files = self.get_pr_files(pr_number)
            diff = ""
            for file in files:
                file_path = file.get("filename")
                status = file.get("status")
                patch = file.get("patch")
                if not patch:
                    continue
                changed_lines = parse_new_lines(patch)
                # TODO too many api calls if there are many files
                file_lines = self.get_file_content(file_path, head_sha).split('\n')
                if not file_lines:
                    continue
                for line in changed_lines:
                    approx_line = line.get("line")
                    target = line.get("content")
                    line["line"] = get_new_file_line_number(file_lines, target, approx_line)
                changed_lines = prepare_changed_lines_text(changed_lines)
                diff += f"File: {file_path}\nStatus: {status}\nChanged lines:\n{changed_lines}\n\n"
            return diff
        except Exception as e:
            logger.exception(f"Error while fetching PR diff for {self.owner}/{self.repo}#{pr_number}")
            raise ValueError(f"Error while fetching PR diff for {self.owner}/{self.repo}#{pr_number}: {str(e)}")
