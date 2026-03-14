from fastapi import APIRouter

router = APIRouter()


@router.post('/github-webhook')
def github_webhook(payload: dict):
    # Process the payload as needed
    print("Received GitHub webhook payload:", payload)
    return {"message": "Webhook received successfully"}