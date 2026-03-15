from app.utils.constants import GitHubWHAction


class IssueCommentEventHandler(object):

    def handle(self, payload):
        action = payload.get("action")

        if action != GitHubWHAction.CREATED:
            return

        if not payload.get("issue", {}).get("pull_request"):
            return

        comment = payload.get("comment", {}).get("body")

        if "@ReviewPilot re-review" in comment:
            print(f"Re-review comment detected... Re-reviewing the PR...\n")
        elif "@ReviewPilot review" in comment:
            print(f"Review comment detected... Reviewing the PR...\n")
        elif "@ReviewPilot summarize" in comment:
            print(f"Summarize comment detected... Summarizing the PR...\n")

