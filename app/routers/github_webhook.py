from fastapi import APIRouter
from app.utils.constants import GitHubWHAction
from app.utils.install_token_gen import get_installation_token

router = APIRouter()


@router.post('/github-webhook')
def github_webhook(payload: dict):
    print("Received GitHub webhook payload:", payload)

    if payload.get("action") == GitHubWHAction.CREATED:
        installation_id = payload.get("installation", {}).get("id")
        # client_id = payload.get("client_id")
        if not installation_id:
            return {"error": "Installation ID not found in payload"}
        installation_token = get_installation_token(installation_id)
        # TODO set installation token in the cache for 10 mins and regenerate if expired
        print(f"Installation Token: {installation_token}\n")
        access_tokens_url = payload.get("access_tokens_url")
        permissions = payload.get("permissions")
        events = payload.get("events")
        repositories = payload.get("repositories")
        repo_full_names = [repo.get("full_name") for repo in repositories]
        print(f"Access tokens url: {access_tokens_url}\n")
        print(f"Permissions: {permissions}\n")
        print(f"Events: {events}\n")
        print(f"Repositories: {repo_full_names}\n")
        '''
        if event == "pull_request" and action == "opened":
            run_ai_review()
        
        elif event == "pull_request" and action == "synchronize":
            re_review_changes()
        
        elif event == "pull_request" and action == "closed" and merged:
            update_repo_embeddings()
        '''


    return {"message": "Webhook processed successfully", "status": "success"}