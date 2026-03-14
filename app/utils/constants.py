from enum import Enum


class GitHubWHAction(str, Enum):
    CREATED = "created"
    OPENED = "opened"
    CLOSED = "closed"


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class Routes(str, Enum):
    GITHUB_WEBHOOK = '/github-webhook'


class BaseUrl(str, Enum):
    GITHUB_API = "https://api.github.com"


class RouteValues(str, Enum):
    INSTALLATION_ACCESS_TOKEN= "/app/installations/{installation_id}/access_tokens"