from app.core.logger import logger
from app.core.utils.constants import GitHubRoutes, HTTPMethod
from app.integrations.github.client import GitHubClient
from app.integrations.github.repo_service import RepoService


class PrService:

    def __init__(self, owner, repo, client: GitHubClient):
        self.owner = owner
        self.repo = repo
        self.repo_service = RepoService(owner, repo, client)
        self.client = client

    def get_pr(self, pr_number):
        """
        :param pr_number:
        :return:
        """
        try:
            path = GitHubRoutes.GET_PR.value.format(owner=self.owner, repo=self.repo, pull_number=pr_number)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                return body
            # TODO check logs
            logger.error("Failed to fetch PR details for %s/%s#%s: status=%s body=%s",
                         self.owner, self.repo, pr_number, status, body)
            print(f"Failed to fetch PR details for {self.owner}/{self.repo}#{pr_number}: status={status} body={body}")
            raise ValueError(f"Failed to fetch PR details for {self.owner}/{self.repo}#{pr_number}: status={status}")

        except Exception:
            # TODO check logs
            logger.exception("Error while fetching PR details for %s/%s#%s", self.owner, self.repo, pr_number)
            raise


    def get_pr_files(self, pr_number):
        """
        :param pr_number:
        :return:
        """
        try:
            path = GitHubRoutes.GET_PR_FILES.value.format(owner=self.owner, repo=self.repo, pull_number=pr_number)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                response = []
                for file in body:
                    filename = file.get("filename")
                    patch = file.get("patch")
                    status = file.get("status")
                    response.append({"filename": filename, "patch": patch, "status": status})
                return response
            # TODO check logs
            logger.error("Failed to fetch PR file details for %s/%s#%s: status=%s body=%s",
                         self.owner, self.repo, pr_number, status, body)
            raise ValueError(
                f"Failed to fetch PR file details for {self.owner}/{self.repo}#{pr_number}: status={status}")

        except Exception:
            # TODO check logs
            logger.exception("Error while fetching PR file details for %s/%s#%s", self.owner, self.repo, pr_number)
            raise


