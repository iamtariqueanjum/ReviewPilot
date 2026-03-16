import logging

from fastapi import APIRouter, Request, status

from app.utils.constants import APIEndpoints
from app.utils.security_util import verify_github_webhook
from app.webhook.event_dispatcher import WebhookEventDispatcher


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(APIEndpoints.GITHUB_WEBHOOK, tags=["webhook"], status_code=status.HTTP_204_NO_CONTENT)
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

    WebhookEventDispatcher().dispatch(event, payload)

    return {"message": "Webhook processed successfully", "status": "success"}