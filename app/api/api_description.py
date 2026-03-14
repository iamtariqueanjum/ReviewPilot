from enum import Enum

class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


class GitHubAPIRoutes(str, Enum):
    ACCESS_TOKEN = "/app/installations/{installation_id}/access_tokens"
