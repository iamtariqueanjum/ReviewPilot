from app.core.utils.constants import GitHubWHAction, GitHubBot
from app.core.utils.input_validator import InputValidator


class IssueCommentEventHandler(object):

    def __init__ (self):
        self.validator = InputValidator()

    def handle(self, payload):
        action = payload.get("action")

        if action == GitHubWHAction.CREATED:
            self.on_created(payload)

    def on_created(self, payload):
        comment = payload.get("comment", {}).get("body")
        if comment.startswith("@"+GitHubBot.USERNAME.value):
            result = self.validator.validate(comment)

            if not result.is_safe:
                reason = result.reason

            # TODO LLM worker integration

