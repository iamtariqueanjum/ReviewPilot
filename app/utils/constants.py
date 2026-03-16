from enum import Enum


class GitHubWHAction(str, Enum):
    CREATED = "created"
    DELETED = "deleted"
    OPENED = "opened"
    REOPENED = "reopened"
    CLOSED = "closed"
    SYNCHRONIZE = "synchronize"


class GitHubWHEvent(str, Enum):
    INSTALLATION = "installation"
    PULL_REQUEST = "pull_request"
    ISSUE_COMMENT = "issue_comment"
    PUSH = "push"


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class GitHubRoutes(str, Enum):
    INSTALLATION_ACCESS_TOKEN = "/app/installations/{installation_id}/access_tokens"
    GET_PR = "/repos/{owner}/{repo}/pulls/{pull_number}"
    GET_PR_FILES = "/repos/{owner}/{repo}/pulls/{pull_number}/files"
    GET_FILE_CONTENT = "/repos/{owner}/{repo}/contents/{path}"
    POST_COMMENT = "/repos/{owner}/{repo}/issues/{issue_number}/comments"


class APIEndpoints(str, Enum):
    GITHUB_WEBHOOK = '/github-webhook'
    REVIEW_PR = "/review-pr"



class BaseUrls(str, Enum):
    GITHUB_API = "https://api.github.com"
    APP_BASE_API = "https://untyrannised-unfoamed-meryl.ngrok-free.dev"