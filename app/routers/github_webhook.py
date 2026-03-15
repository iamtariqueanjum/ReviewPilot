import logging

from fastapi import APIRouter, Request

from app.utils.constants import GitHubWHAction, Routes
from app.utils.security_util import verify_github_webhook


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(Routes.GITHUB_WEBHOOK)
async def github_webhook(request: Request):
    body = await request.body()
    payload = await request.json()

    signature = request.headers.get("x-hub-signature-256")
    event = request.headers.get("x-github-event")
    print(f"Received GitHub webhook event: {event}\n")
    print(f"Payload: {payload}\n")
    print(f"Body: {body}\n")

    if not verify_github_webhook(body, signature):
        return {"error": "Invalid webhook signature", "status": "error"}

    if payload.get("action") == GitHubWHAction.CREATED:
        installation = payload.get("installation")
        installation_id = installation.get("id")
        print(f"Installation ID: {installation_id}")
        if not installation_id:
            return {"error": "Installation ID not found in payload", "status": "error"}

        # if event == "pull_request":
        #     handle_pr_event(payload)
        #
        # elif event == "push":
        #     handle_push_event(payload)
        #
        # elif event == "installation":
            # repositories = payload.get("repositories")
            # repo_full_names = [repo.get("full_name") for repo in repositories]
            # print(f"Repositories: {repo_full_names}\n")
        #     handle_installation_event(payload)

        # if event == "pull_request" and action == "opened":
        #     run_ai_review()
        #
        # elif event == "pull_request" and action == "synchronize":
        #     re_review_changes()
        #
        # elif event == "pull_request" and action == "closed" and merged:
        #     update_repo_embeddings()


    return {"message": "Webhook processed successfully", "status": "success"}