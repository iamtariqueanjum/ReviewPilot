from app.core.utils.constants import GitHubRoutes, HTTPMethod
from app.integrations.github.client import GitHubClient
from app.integrations.logger import logger


class CommentService:

    def __init__(self, owner, repo, client: GitHubClient):
        self.owner = owner
        self.repo = repo
        self.client = client

    def post_comment(self, issue_number, comment):
        """
        :param issue_number:
        :param comment:
        :return:
        """
        try:
            path = GitHubRoutes.POST_COMMENT.value.format(owner=self.owner, repo=self.repo, issue_number=issue_number)
            result = self.client.call_api(HTTPMethod.POST, path, json={"body": comment})
            status = result.get("status_code")
            body = result.get("body")
            if status and 200 <= status < 300:
                logger.info("Successfully posted comment to %s/%s/%s", self.owner, self.repo, issue_number)
                return body
            logger.error("Failed to post comment for %s/%s#%s: status=%s body=%s",
                         self.owner, self.repo, issue_number, status, body)
            raise ValueError(f"Failed to post comment for {self.owner}/{self.repo}#{issue_number}: status={status}")
        except Exception:
            logger.exception("Error while posting comment for %s/%s#%s", self.owner, self.repo, issue_number)
            raise
