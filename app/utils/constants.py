from enum import Enum

from app.config.provider import get_config
settings = get_config()


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


class LLMProvider(str, Enum):
    OPENAI = "openai"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"
    CUSTOM = "custom"


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class GitHubRoutes(str, Enum):
    INSTALLATION_ACCESS_TOKEN = "/app/installations/{installation_id}/access_tokens"
    GET_PR = "/repos/{owner}/{repo}/pulls/{pull_number}"
    GET_PR_FILES = "/repos/{owner}/{repo}/pulls/{pull_number}/files"
    GET_FILE_CONTENT = "/repos/{owner}/{repo}/contents/{path}?ref={head_sha}"
    POST_COMMENT = "/repos/{owner}/{repo}/issues/{issue_number}/comments"


class APIEndpoints(str, Enum):
    GITHUB_WEBHOOK = '/github-webhook'
    REVIEW_PR = "/review-pr"


class ConfigConstants(str, Enum):
    # LLM-related
    DEFAULT_LLM_PROVIDER = settings.DEFAULT_LLM_PROVIDER
    OPENAI_BASE_MODEL = settings.OPENAI_BASE_MODEL
    GEMINI_BASE_MODEL = settings.GEMINI_BASE_MODEL
    GEMINI_API_KEY = settings.GEMINI_API_KEY

    # GitHub-related
    GITHUB_APP_ID = settings.GITHUB_APP_ID
    GITHUB_PRIVATE_KEY_PATH = settings.GITHUB_PRIVATE_KEY_PATH
    GITHUB_WEBHOOK_SECRET = settings.GITHUB_WEBHOOK_SECRET

    # App-related
    GITHUB_API = settings.GITHUB_API
    INTERNAL_API = settings.INTERNAL_API
