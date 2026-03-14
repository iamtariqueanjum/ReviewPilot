from enum import Enum


class GitHubWHAction(str, Enum):
    CREATED = "created"
    OPENED = "opened"
    CLOSED = "closed"

