from app.utils.constants import GitHubWHEvent

from app.event_handlers.installation_event_handler import InstallationEventHandler
from app.event_handlers.issue_comment_event_handler import IssueCommentEventHandler
from app.event_handlers.pull_request_event_handler import PullRequestEventHandler
from app.event_handlers.push_event_handler import PushEventHandler


class WebhookEventDispatcher(object):

    def __init__(self):
        self.handlers = {
            GitHubWHEvent.PULL_REQUEST: PullRequestEventHandler(),
            GitHubWHEvent.INSTALLATION: InstallationEventHandler(),
            GitHubWHEvent.ISSUE_COMMENT: IssueCommentEventHandler(),
            GitHubWHEvent.PUSH: PushEventHandler()
        }

    def dispatch(self, event, payload):
        handler = self.handlers.get(event)

        if not handler:
            return {"error": f"Event {event} not found", "status": "error" }

        return handler.handle(payload)
