import logging

from fastapi import APIRouter, Request

from app.utils.constants import Routes
from app.utils.security_util import verify_github_webhook
from app.event_handlers.webhook_event_dispatch import WebhookEventDispatcher


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

    WebhookEventDispatcher().dispatch(event, payload)

    return {"message": "Webhook processed successfully", "status": "success"}