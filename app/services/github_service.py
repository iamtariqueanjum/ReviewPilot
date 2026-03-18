import base64

from app.core.logger import logger
from app.integrations.github.client import GitHubClient
from app.utils.constants import GitHubRoutes, HTTPMethod


class GithubService(object):

    def __init__(self, installation_id):
        self.client = GitHubClient(installation_id)

    def get_pr(self, owner, repo, pr_number):
        """
        :param owner:
        :param repo:
        :param pr_number:
        :return:
        """
        try:
            path = GitHubRoutes.GET_PR.value.format(owner=owner, repo=repo, pull_number=pr_number)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                return body
            # TODO check logs
            logger.error("Failed to fetch PR details for %s/%s#%s: status=%s body=%s",
                         owner, repo, pr_number, status, body)
            print(f"Failed to fetch PR details for {owner}/{repo}#{pr_number}: status={status} body={body}")
            raise ValueError(f"Failed to fetch PR details for {owner}/{repo}#{pr_number}: status={status}")

        except Exception:
            # TODO check logs
            logger.exception("Error while fetching PR details for %s/%s#%s", owner, repo, pr_number)
            raise

    def get_pr_files(self, owner, repo, pr_number):
        """
        :param owner:
        :param repo:
        :param pr_number:
        :return:
        """
        try:
            path = GitHubRoutes.GET_PR_FILES.value.format(owner=owner, repo=repo, pull_number=pr_number)
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
                         owner, repo, pr_number, status, body)
            raise ValueError(f"Failed to fetch PR file details for {owner}/{repo}#{pr_number}: status={status}")

        except Exception:
            # TODO check logs
            logger.exception("Error while fetching PR file details for %s/%s#%s", owner, repo, pr_number)
            raise

    def get_file_content(self, owner, repo, path, head_sha=None):
        """
        :param owner:
        :param repo:
        :param path: file_path example: src/app/main.py
        :param head_sha:
        :return:
        """
        try:
            path = GitHubRoutes.GET_FILE_CONTENT.value.format(owner=owner, repo=repo, path=path, head_sha=head_sha)
            result = self.client.call_api(HTTPMethod.GET, path)
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                return base64.b64decode(body.get("content", "")).decode("utf-8")

            if status and status == 404:
                logger.warning("File content not found for %s/%s#%s: status=%s body=%s",
                               owner, repo, path, status, body)
                return ""

            # TODO check logs
            logger.error("Failed to fetch PR file content for %s/%s#%s: status=%s body=%s",
                         owner, repo, path, status, body)
            raise ValueError(f"Failed to fetch PR file content for {owner}/{repo}#{path}: status={status}")

        except Exception:
            # TODO check logs
            logger.exception("Error while fetching PR file content for %s/%s#%s", owner, repo, path)
            raise

    def post_comment(self, owner, repo, issue_number, comment):
        try:
            path = GitHubRoutes.POST_COMMENT.value.format(owner=owner, repo=repo, issue_number=issue_number)
            result = self.client.call_api(HTTPMethod.POST, path, json={"body": comment})
            status = result.get("status_code")
            body = result.get("body")

            if status and 200 <= status < 300:
                print(f"Successfully posted comment for {owner}/{repo}#{issue_number}: {comment}")
                print(f"GitHub response: status={status} body={body}")
                return body
            # TODO check logs
            logger.error("Failed to post comment for %s/%s#%s: status=%s body=%s",
                         owner, repo, issue_number, status, body)
            print(f"Failed to post comment for {owner}/{repo}#{issue_number}: status={status} body={body}")
            raise ValueError(f"Failed to post comment for {owner}/{repo}#{issue_number}: status={status}")
        except Exception:
            # TODO check logs
            logger.exception("Error while posting comment for %s/%s#%s", owner, repo, issue_number)
            raise


