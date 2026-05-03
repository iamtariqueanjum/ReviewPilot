import base64

from app.core.logger import logger
from app.core.utils.constants import GitHubRoutes, HTTPMethod
from app.integrations.github.client import GitHubClient


class RepoService:

    def __init__(self, owner, repo, client: GitHubClient):
        self.owner = owner
        self.repo = repo
        self.client = client

    def get_repository(self):
        """
        :return:
        """
        try:
            path = GitHubRoutes.GET_REPOSITORY.value.format(owner=self.owner, repo=self.repo)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                print(f"Successfully retrieved repo details for {self.owner}/{self.repo}")
                print(f"GitHub response: status={status} body={body}")
                return body
            # TODO check logs
            logger.error("Failed to retrieve repo details for %s/%s: status=%s body=%s",
                         self.owner, self.repo, status, body)
            print(f"Failed to retrieve repo details for {self.owner}/{self.repo}: status={status} body={body}")
            raise ValueError(f"Failed to retrieve repo details for {self.owner}/{self.repo}: status={status}")
        except Exception:
            # TODO check logs
            logger.exception("Error while retrieving repo details for %s/%s", self.owner, self.repo)
            raise

    def get_branch(self, branch):
        """
        :param branch:
        :return:
        """
        try:
            path = GitHubRoutes.GET_BRANCH.value.format(owner=self.owner, repo=self.repo, branch=branch)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                print(f"Successfully retrieved branch details for {self.owner}/{self.repo}/{branch}")
                print(f"GitHub response: status={status} body={body}")
                return body
            # TODO check logs
            logger.error("Failed to retrieve branch details for %s/%s/%s: status=%s body=%s",
                         self.owner, self.repo, branch, status, body)
            print(f"Failed to retrieve branch details for {self.owner}/{self.repo}/{branch}: status={status} body={body}")
            raise ValueError(f"Failed to retrieve branch details for {self.owner}/{self.repo}/{branch}: status={status}")
        except Exception:
            # TODO check logs
            logger.exception("Error while retrieving branch details for %s/%s/%s", self.owner, self.repo, branch)
            raise

    def get_tree_recursive(self, tree_sha):
        """
        :param tree_sha:
        :return:
        """
        try:
            path = GitHubRoutes.GET_TREE_RECURSIVE.value.format(owner=self.owner, repo=self.repo, tree_sha=tree_sha)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                print(f"Successfully retrieved tree details for {self.owner}/{self.repo}/{tree_sha}")
                print(f"GitHub response: status={status} body={body}")
                return body
            # TODO check logs
            logger.error("Failed to retrieve tree details for %s/%s/%s: status=%s body=%s",
                         self.owner, self.repo, tree_sha, status, body)
            print(f"Failed to retrieve tree details for {self.owner}/{self.repo}/{tree_sha}: status={status} body={body}")
            raise ValueError(f"Failed to retrieve tree details for {self.owner}/{self.repo}/{tree_sha}: status={status}")
        except Exception:
            # TODO check logs
            logger.exception("Error while retrieving tree details for %s/%s/%s", self.owner, self.repo, tree_sha)
            raise

    def get_file_content(self, path, head_sha=None):
        """
        :param path: file_path example: src/app/main.py
        :param head_sha:
        :return:
        """
        try:
            path = GitHubRoutes.GET_FILE_CONTENT.value.format(owner=self.owner, repo=self.repo, path=path, head_sha=head_sha)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                return base64.b64decode(body.get("content", "")).decode("utf-8")

            if status and status == 404:
                logger.warning("File content not found for %s/%s#%s: status=%s body=%s",
                               self.owner, self.repo, path, status, body)
                return ""

            # TODO check logs
            logger.error("Failed to fetch PR file content for %s/%s#%s: status=%s body=%s",
                         self.owner, self.repo, path, status, body)
            raise ValueError(f"Failed to fetch PR file content for {self.owner}/{self.repo}#{path}: status={status}")

        except Exception:
            # TODO check logs
            logger.exception("Error while fetching PR file content for %s/%s#%s", self.owner, self.repo, path)
            raise

    def get_blob_content(self, file_sha):
        """
        :param file_sha:
        :return:
        """
        try:
            path = GitHubRoutes.GET_BLOB_CONTENT.value.format(owner=self.owner, repo=self.repo, file_sha=file_sha)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                print(f"Successfully retrieved blob content for {self.owner}/{self.repo}/{file_sha}")
                print(f"GitHub response: status={status} body={body}")
                return base64.b64decode(body.get("content", "")).decode("utf-8")
            # TODO check logs
            logger.error("Failed to retrieve blob content for %s/%s/%s: status=%s body=%s",
                         self.owner, self.repo, file_sha, status, body)
            print(f"Failed to retrieve blob content for {self.owner}/{self.repo}/{file_sha}: status={status} body={body}")
            raise ValueError(f"Failed to retrieve blob content for {self.owner}/{self.repo}/{file_sha}: status={status}")
        except Exception:
            # TODO check logs
            logger.exception("Error while retrieving blob content for %s/%s/%s", self.owner, self.repo, file_sha)
            raise