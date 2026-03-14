import logging

from fastapi import APIRouter, Request
from app.utils.constants import GitHubWHAction
from app.utils.install_token_gen import get_installation_token
from app.utils.security_util import verify_github_webhook


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post('/github-webhook')
async def github_webhook(request: Request):
    print("Received GitHub webhook payload:\n")
    print(f"Headers: {request.headers}\n")
    body = await request.body()
    print(f"Body: {body}\n")
    payload = await request.json()
    print(f"Json: {payload}\n")

    signature = request.headers.get("x-hub-signature-256")
    event = request.headers.get("x-github-event")
    print(f"Webhook signature: {signature}\n")
    print(f"Webhook event: {event}\n")

    if not verify_github_webhook(body, signature):
        raise Exception("Invalid webhook signature")

    if payload.get("action") == GitHubWHAction.CREATED:
        installation = payload.get("installation")
        installation_id = installation.get("id")
        # client_id = payload.get("client_id")
        if not installation_id:
            return {"error": "Installation ID not found in payload"}
        installation_token = get_installation_token(installation_id)
        # TODO set installation token in the cache for 10 mins and regenerate if expired
        print(f"Installation Token: {installation_token}\n")
        access_tokens_url = installation.get("access_tokens_url")
        permissions = installation.get("permissions")
        events = installation.get("events")
        repositories = payload.get("repositories")
        repo_full_names = [repo.get("full_name") for repo in repositories]
        print(f"Access tokens url: {access_tokens_url}\n")
        print(f"Permissions: {permissions}\n")
        print(f"Events: {events}\n")
        print(f"Repositories: {repo_full_names}\n")
        '''
        if event == "pull_request":
            handle_pr_event(payload)
        
        elif event == "push":
            handle_push_event(payload)
        
        elif event == "installation":
            handle_installation_event(payload)
                 
                if event == "pull_request" and action == "opened":
                    run_ai_review()
                
                elif event == "pull_request" and action == "synchronize":
                    re_review_changes()
                
                elif event == "pull_request" and action == "closed" and merged:
                    update_repo_embeddings()
        '''


    return {"message": "Webhook processed successfully", "status": "success"}