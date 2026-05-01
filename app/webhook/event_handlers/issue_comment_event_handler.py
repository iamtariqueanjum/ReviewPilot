from app.core.utils.constants import GitHubWHAction, GitHubBot, QueueConstants
from app.core.utils.input_validator import InputValidator
from app.workers.chatbot_worker import process_chat_message


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
                print("Reason:", reason)
                return

            query = result.sanitized_input

            owner = payload.get("repository", {}).get("full_name", "").split("/")[0]
            repo = payload.get("repository", {}).get("full_name", "").split("/")[1]
            pr_number = payload.get("issue", {}).get("number")
            comment_id = payload.get("comment", {}).get("id")
            installation_id = payload.get("installation", {}).get("id")
            sender = payload.get("sender", {}).get("login")

            query_id = f"{repo}_{pr_number}_{comment_id}"

            process_chat_message.apply_async(
                task_id=query_id,
                args=(installation_id, owner, repo, pr_number, sender, query),
                countdown=10,
                retry=True,
                queue=QueueConstants.CHAT_MESSAGES_QUEUE
            )
            print(f"Query pushed to queue {query_id}\n")
