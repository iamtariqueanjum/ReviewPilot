from enum import Enum


class GitHubWHAction(str, Enum):
    CREATED = "created"
    OPENED = "opened"
    CLOSED = "closed"


class Routes(str, Enum):
    GITHUB_WEBHOOK = '/github-webhook'


class BaseUrl(str, Enum):
    GITHUB_API = "https://api.github.com"
